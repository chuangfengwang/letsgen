# -*- coding: utf-8 -*-
"""
# @File    : pg_log_search_dao.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2026-02-26 23:48
"""
import asyncio
import json

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import letsgen.db.pg_connection as pg_connection


async def adaptive_search(self, query_text: str, category_id: int, target: int = 10):
    """
    实现自适应阶梯召回策略
    1. 快速路径：直接利用 BM25 索引进行过召回 (Limit 5x)
    2. 深度路径：如果快速路径未凑齐结果，根据分数判断是“真没货”还是“被截断”
    """
    # --- 第一步：快速路径 (利用 Block-Max WAND 的高速) ---
    # 尝试索取 5 倍的数据，期待其中能凑够 target 条符合 category_id 的
    fast_query = """
                 SELECT id, content, content <@> $1 AS rank
                 FROM docs
                 WHERE category_id = $2
                 ORDER BY rank ASC
                 LIMIT $3; \
                 """

    db_engine = await pg_connection.async_db_pg_engine()

    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        over_limit = int(target * 5)
        # 注意：pg_textsearch 的 <@> 返回负分，相关性越高，数值越小
        rows = await session.fetch(fast_query, query_text, category_id, over_limit)

        # 提取真正“命中的”结果 (rank < 0)
        valid_hits = [r for r in rows if r['rank'] < 0]

        # 情况 A: 结果已经足够
        if len(valid_hits) >= target:
            return valid_hits[:target]

        # 情况 B: 结果不足，判断是否需要“深度补偿”
        # 如果 rows 为空，或者最后一条结果的 rank 已经接近 0
        # 说明索引已经把包含关键词的文档扫完了，全库真的只有这么多
        is_exhausted = len(rows) < (target * 5) or (rows and rows[-1]['rank'] >= -0.0001)

        if is_exhausted:
            return valid_hits

        # --- 第二步：深度路径 (当过滤掉太多，需要更深度的检索) ---
        # 此时我们已知：有更多相关的文档，但被 category_id 挡在了前 5*target 之外
        # 我们使用子查询或扩大 Limit 的方式进行补偿
        print(f"触发深度补偿逻辑: 当前仅找到 {len(valid_hits)} 条")

        deep_query = """
                     SELECT * \
                     FROM (SELECT id, content, content <@> $1 AS rank \
                           FROM docs \
                           WHERE category_id = $2 \
                             AND content <@> to_bm25query($1, 'docs_idx') < 0) sub
                     ORDER BY rank ASC
                     LIMIT $3; \
                     """
        # 这里的 LIMIT 直接给 target，因为子查询内部已经把不相关的全过滤了
        deep_rows = await self.pool.fetch(deep_query, query_text, category_id, target)
        return deep_rows


async def optimized_high_limit_search(self, query_text: str, cat_id: int, target: int = 500):
    # 1. 第一次尝试：稍微多取一点（比如 1.5 倍）
    # 在高 LIMIT 下，我们直接把 rank < 0 的过滤下推到索引层
    initial_limit = int(target * 1.5)

    # 这里的关键是使用 to_bm25query，虽然可能让 WAND 稍慢，
    # 但由于它在索引扫描时就排除了不相关的行，能保证 LIMIT 的有效性
    try_query = """
                SELECT id, content, content <@> $1 AS rank
                FROM docs
                WHERE category_id = $2
                  AND content <@> to_bm25query($1, 'docs_idx') < 0
                ORDER BY rank ASC
                LIMIT $3; \
                """

    db_engine = await pg_connection.async_db_pg_engine()

    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        rows = await session.fetch(try_query, query_text, cat_id, initial_limit)

        # 如果已经够了，直接返回
        if len(rows) >= target:
            return rows[:target]

        # 2. 如果不够，说明该 category 下相关文档确实很少，直接去掉 LIMIT 限制取剩余全部
        # 因为既然 initial_limit 都没填满，说明总量本身就不大，全量扫描压力也不大

        return rows


class AdvancedBM25Searcher:
    def __init__(self, dsn):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            self.dsn,
            min_size=5,
            max_size=20,
            # 设置初始参数，优化搜索性能
            init=self._setup_connection
        )

    async def _setup_connection(self, conn):
        # 针对搜索会话优化内存，确保大 LIMIT 排序不在磁盘进行
        await conn.execute("SET work_mem = '64MB'")
        # 确保 pg_textsearch 的默认限制足够大
        await conn.execute("SET pg_textsearch.default_limit = 5000")

    async def search_with_hits(self, query_text: str, cat_id: int, target: int = 500):
        """
        核心函数：自适应召回 + 类似 ES 的 hits 统计
        """
        async with self.pool.acquire() as conn:
            # 1. 估算总数 (类似 ES 的非精确 hits)
            # 使用 EXPLAIN 预估行数，不消耗 IO
            explain_query = f"""
                EXPLAIN (FORMAT JSON)
                SELECT 1 FROM documents 
                WHERE category_id = $1 
                  AND content <@> to_bm25query($2, 'docs_idx') < 0
            """
            plan_json = await conn.fetchval(explain_query, cat_id, query_text)
            estimated_total = json.loads(plan_json)[0]['Plan']['Plan Rows']

            # 2. 阶梯召回 - 快速路径 (针对高 LIMIT 优化)
            # 当 target 较大时，我们不再用 5 倍过召回，而是用 1.2 倍以保护 CPU
            fast_limit = int(target * 1.2)

            # 这里的 WHERE 条件使用了索引下推，确保返回的都是有命中的
            main_sql = """
                       SELECT id, title, content <@> $1 AS rank
                       FROM docs
                       WHERE category_id = $2
                         AND content <@> to_bm25query($1, 'docs_idx') < 0
                       ORDER BY rank ASC
                       LIMIT $3 \
                       """

            rows = await conn.fetch(main_sql, query_text, cat_id, fast_limit)

            # 3. 结果评估与自适应补齐
            final_results = rows
            is_accurate_total = False
            actual_total = estimated_total

            # 如果拿到的数据量少于 fast_limit，说明全库符合条件的文档已经拿完了
            if len(rows) < fast_limit:
                is_accurate_total = True
                actual_total = len(rows)
            # 如果拿到的数据多于或等于 target，直接截断返回
            elif len(rows) >= target:
                final_results = rows[:target]

            # 4. 构建类似 ES 的返回结构
            return {
                "hits": {
                    "total": {
                        "value": actual_total,
                        "relation": "eq" if is_accurate_total else "gte"  # gte 表示“大于等于”
                    },
                    "hits": [dict(r) for r in final_results]
                },
                "timed_out": False,
                "estimated": not is_accurate_total
            }


# --- 运行示例 ---
async def run_demo():
    # 替换为你的真实 DSN
    DSN = "postgresql://postgres:password@localhost:5432/search_db"
    searcher = AdvancedBM25Searcher(DSN)
    await searcher.connect()

    # 模拟一个 LIMIT 500 的查询
    response = await searcher.search_with_hits("高性能 数据库 调优", cat_id=101, target=500)

    total = response['hits']['total']
    print(f"搜索结果: 找到 {total['value']} {('条' if total['relation'] == 'eq' else '条以上')}")

    for hit in response['hits']['hits'][:3]:
        print(f" -> [Score: {hit['rank']:.2f}] ID: {hit['id']}")


if __name__ == "__main__":
    asyncio.run(run_demo())

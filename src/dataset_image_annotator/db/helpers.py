import logging
from typing import Mapping

import sqlalchemy as sa
from sqlalchemy import desc, asc, func
from sqlalchemy.sql.elements import BooleanClauseList, UnaryExpression

logger = logging.getLogger()


def get_query(search: Mapping[str, str] | None = None,
              order_by: str | None = None,
              columns: Mapping | None = None) -> tuple[BooleanClauseList, UnaryExpression]:
    """
        :columns:
            0: Model column
            1: case-insensitive if True
            2: cast value to type
            3: exact match if True, LIKE %value% if False
    """
    if order_by:
        if order_by.startswith('-'):
            direction = desc
            order_by = order_by[1:]
        else:
            direction = asc

        order_by_clause = direction(columns[order_by][0])
    else:
        order_by_clause = None

    if search:
        where_parts = [
            *(
                (func.upper(columns[k][0])
                 if columns[k][1]
                 else columns[k][0]
                 ) == columns[k][2](v)
                for k, v in search.items()
                if columns[k][3]
            ),
            *(
                (func.upper(columns[k][0])
                 if columns[k][1]
                 else columns[k][0]
                 ).like(f'%{v.upper()}%')
                for k, v in search.items()
                if not columns[k][3]
            )
        ]
    else:
        where_parts = None

    if where_parts:
        where_clause = sa.and_(*where_parts)
    else:
        where_clause = None

    return where_clause, order_by_clause

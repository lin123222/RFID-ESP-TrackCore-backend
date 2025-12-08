"""remove_nickname_and_status_fields

Revision ID: 001
Revises: 
Create Date: 2024-12-08 10:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 删除 nickname 字段
    op.drop_column('users', 'nickname')
    
    # 删除 status 字段
    op.drop_column('users', 'status')


def downgrade() -> None:
    # 恢复 status 字段
    op.add_column('users', 
        sa.Column('status', mysql.INTEGER(), nullable=False, server_default='1')
    )
    # 添加注释（MySQL 需要单独执行）
    op.execute("ALTER TABLE users MODIFY COLUMN status INT DEFAULT 1 NOT NULL COMMENT '状态: 1正常 0禁用'")
    
    # 恢复 nickname 字段
    op.add_column('users',
        sa.Column('nickname', mysql.VARCHAR(length=100), nullable=True)
    )
    # 添加注释（MySQL 需要单独执行）
    op.execute("ALTER TABLE users MODIFY COLUMN nickname VARCHAR(100) NULL COMMENT '昵称'")


from sqlalchemy.dialects.postgresql import ENUM
from enum import Enum


class PagingType(Enum):
    CURSOR = 'CURSOR'
    OFFSET = 'OFFSET'


user_prefix_enum = ENUM(
    'Miss', 'Mr', 'Mrs', 'Ms', 'Mx', name='user_prefix_enum')

user_status_enum = ENUM(
    'Active', 'Banned', 'Inactive', 'Pending', name='user_status_enum')

import sys
sys.path.insert(0, r'C:\Users\mmksy\OneDrive\Рабочий стол\3 проект')
from data.db_session import SqlAlchemyBase
import data.__all_models
target_metadata = SqlAlchemyBase.metadata
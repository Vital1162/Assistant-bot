from datetime import datetime
import pytz



timezone = pytz.timezone("Asia/Ho_Chi_Minh")
local_time = datetime.now(timezone)
current_time = local_time.strftime("%I:%M:%S%p")


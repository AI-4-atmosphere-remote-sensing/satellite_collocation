import os
import datetime
from datetimerange import DateTimeRange



abi_name = os.path.basename("OR_ABI-L1b-RadF-M3C02_G16_s20190400030316_e20190400041083_c20190400041127.nc")
abi_start_pos = abi_name.find("_s")
abi_end_pos = abi_name.find("_e")
abi_starttimeflag = abi_name[abi_start_pos+2:abi_start_pos+15]
abi_endtimeflag = abi_name[abi_end_pos+2:abi_end_pos+15]
abi_sdt = datetime.datetime.strptime(abi_starttimeflag, "%Y%j%H%M%S")
abi_edt = datetime.datetime.strptime(abi_endtimeflag, "%Y%j%H%M%S")
#abi_mdt = abi_sdt + (abi_edt-abi_sdt)/2.
#abi_mdts.append(abi_mdt)
abi_range = DateTimeRange(abi_sdt,abi_edt)

print(abi_range)
#!/bin/bash

timestamp() {
  date +"%s" # current time
}

n_worker=8

timestamp

#cd satellite_collocation/examples/collocate_abi_calipso_local_execution
cd

# #20190101 - 20190110
# for date in {1..9} 
# do
#     for i in {0..9}
#     do
#     python3 collocation_dask_local.py -ap ../../taki_data/OR_ABI-L1b-RadF/00${date}/0${i}/ -ip ../../taki_data/index-output/ -sp ../../taki_data/abi-output/ -nw ${n_worker}
#     done

#     for i in {10..23}
#     do
#     python3 collocation_dask_local.py -ap ../../taki_data/OR_ABI-L1b-RadF/00${date}/${i}/ -ip ../../taki_data/index-output/ -sp ../../taki_data/abi-output/ -nw ${n_worker}
#     done
# done

for date in 10
do
    for i in {0..9}
    do
    #python3 collocation_dask_local.py -ap ../../taki_data/OR_ABI-L1b-RadF/0${date}/0${i}/ -ip ../../taki_data/index-output/ -sp ../../taki_data/abi-output/ -nw ${n_worker}
    python3 satellite_collocation/examples/collocate_abi_calipso_local_execution/collocation_dask_distributed.py -ap satellite_collocation/taki_data/OR_ABI-L1b-RadF/0${date}/0${i}/ -ip satellite_collocation/taki_data/index-output/ -sp satellite_collocation/taki_data/abi-output/ -ds tcp://172.31.56.22:8786
    done

    for i in {10..23}
    do
    #python3 collocation_dask_local.py -ap ../../taki_data/OR_ABI-L1b-RadF/0${date}/${i}/ -ip ../../taki_data/index-output/ -sp ../../taki_data/abi-output/ -nw ${n_worker}
    python3 satellite_collocation/examples/collocate_abi_calipso_local_execution/collocation_dask_distributed.py -ap satellite_collocation/taki_data/OR_ABI-L1b-RadF/0${date}/${i}/ -ip satellite_collocation/taki_data/index-output/ -sp satellite_collocation/taki_data/abi-output/ -ds tcp://172.31.56.22:8786
    done
done

# #20190201 - 20190209
# for date in {32..40}
# do
#     for i in {0..9}
#     do
#     python3 collocation_dask_local.py -ap ../../taki_data/OR_ABI-L1b-RadF/0${date}/0${i}/ -ip ../../taki_data/index-output/ -sp ../../taki_data/abi-output/ -nw ${n_worker}
#     done

#     for i in {10..23}
#     do
#     python3 collocation_dask_local.py -ap ../../taki_data/OR_ABI-L1b-RadF/0${date}/${i}/ -ip ../../taki_data/index-output/ -sp ../../taki_data/abi-output/ -nw ${n_worker}
#     done
# done

timestamp


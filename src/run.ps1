<#Setup
cd ..
pip3 install -r setup/requirements.txt
cd src
#>

<#CessnaSkyhawk
python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Palo Alto" --label --name "starter_dataset2" -ac "Cessna Skyhawk" --newac
if [ $? = 0 ]
then
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Osh Kosh" --label --name "starter_dataset2" -ac "Cessna Skyhawk" --append
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Boston" --label --name "starter_dataset2" -ac "Cessna Skyhawk" --append
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Reno Tahoe" --label --name "starter_dataset2" -ac "Cessna Skyhawk" --append
fi
#>

<#Boeing737-800
python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Palo Alto" --label --name "starter_dataset" -ac "Boeing 737-800" --append --newac
if [ $? = 0 ]
then
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Osh Kosh" --label --name "starter_dataset" -ac "Boeing 737-800" --append
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Boston" --label --name "starter_dataset" -ac "Boeing 737-800" --append
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Reno Tahoe" --label --name "starter_dataset" -ac "Boeing 737-800" --append
fi
#>

<#KingAirC90
python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Palo Alto" --label --name "starter_dataset" -ac "King Air C90" --append --newac
if [ $? = 0 ]
then
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Osh Kosh" --label --name "starter_dataset" -ac "King Air C90" --append
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Boston" --label --name "starter_dataset" -ac "King Air C90" --append
    python -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Reno Tahoe" --label --name "starter_dataset" -ac "King Air C90" --append
fi
#>
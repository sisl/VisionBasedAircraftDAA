<<Setup
cd ..
pip3 install -r setup/requirements.txt
cd src
Setup

<<CessnaSkyhawk
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Palo Alto" --label --name "starter_dataset" -ac "Cessna Skyhawk" --newac
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Osh Kosh" --label --name "starter_dataset" -ac "Cessna Skyhawk" --append
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Boston" --label --name "starter_dataset" -ac "Cessna Skyhawk" --append
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Reno Tahoe" --label --name "starter_dataset" -ac "Cessna Skyhawk" --append
CessnaSkyhawk

<<Boeing737-800
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Palo Alto" --label --name "starter_dataset" -ac "Boeing 737-800" --append --newac
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Osh Kosh" --label --name "starter_dataset" -ac "Boeing 737-800" --append
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Boston" --label --name "starter_dataset" -ac "Boeing 737-800" --append
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Reno Tahoe" --label --name "starter_dataset" -ac "Boeing 737-800" --append
Boeing737-800

#<<KingAirC90
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Palo Alto" --label --name "starter_dataset" -ac "King Air C90" --append --newac
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Osh Kosh" --label --name "starter_dataset" -ac "King Air C90" --append
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Boston" --label --name "starter_dataset" -ac "King Air C90" --append
python3 -m data_generation.generate_traffic_data --train 15 --valid 5 --location "Reno Tahoe" --label --name "starter_dataset" -ac "King Air C90" --append
#KingAirC90
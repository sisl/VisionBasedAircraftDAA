# Add '#' in front of individual lines to comment them out. The phrases preceded by '<<' begin block comments 
# and the end of the block is indicated by the same word without '<<'. Use '#' in front of the '<<' and in front
# of the ending word to uncomment the commands in between. 

#<<TESTING
python3 -m data_generation.generate_traffic_data -aw --label -ac "Cessna Skyhawk" --newac --name "test"
#TESTING

<<CessnaSkyhawk
python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Palo Alto" --label --name "sample_dataset" -ac "Cessna Skyhawk" --newac
if [ $? = 0 ]
then
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --label --name "sample_dataset" -ac "Cessna Skyhawk" --append
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --label --name "sample_dataset" -ac "Cessna Skyhawk" --append
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --label --name "sample_dataset" -ac "Cessna Skyhawk" --append
fi
CessnaSkyhawk

<<Boeing737-800
python3 -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Palo Alto" --label --name "sample_dataset" -ac "Boeing 737-800" --append --newac
if [ $? = 0 ]
then
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --label --name "sample_dataset" -ac "Boeing 737-800" --append
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --label --name "sample_dataset" -ac "Boeing 737-800" --append
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --label --name "sample_dataset" -ac "Boeing 737-800" --append
fi
Boeing737-800

<<KingAirC90
python3 -m data_generation.generate_traffic_data -aw --train 9 --valid 1 --location "Palo Alto" --label --name "sample_dataset" -ac "King Air C90" --append --newac
if [ $? = 0 ]
then
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --label --name "sample_dataset" -ac "King Air C90" --append
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --label --name "sample_dataset" -ac "King Air C90" --append
    python3 -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --label --name "sample_dataset" -ac "King Air C90" --append
fi
KingAirC90
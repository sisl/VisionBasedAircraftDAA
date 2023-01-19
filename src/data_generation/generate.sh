# Add '#' in front of individual lines to comment them out. The phrases preceded by '<<' begin block comments 
# and the end of the block is indicated by the same word without '<<'. Use '#' in front of the '<<' and in front
# of the ending word to uncomment the commands in between. 

#<<TESTING
python3 -m generate_traffic_data -aw -ac "Cessna Skyhawk" --newac --name "sample_small"
#TESTING

<<CessnaSkyhawk
python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Palo Alto" --name "sample_dataset" -ac "Cessna Skyhawk" --newac
if [ $? = 0 ]
then
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --name "sample_dataset" -ac "Cessna Skyhawk" --append
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --name "sample_dataset" -ac "Cessna Skyhawk" --append
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --name "sample_dataset" -ac "Cessna Skyhawk" --append
fi
CessnaSkyhawk

<<Boeing737-800
python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Palo Alto" --name "sample_dataset" -ac "Boeing 737-800" --append --newac
if [ $? = 0 ]
then
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --name "sample_dataset" -ac "Boeing 737-800" --append
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --name "sample_dataset" -ac "Boeing 737-800" --append
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --name "sample_dataset" -ac "Boeing 737-800" --append
fi
Boeing737-800

<<KingAirC90
python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Palo Alto" --name "sample_dataset" -ac "King Air C90" --append --newac
if [ $? = 0 ]
then
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --name "sample_dataset" -ac "King Air C90" --append
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --name "sample_dataset" -ac "King Air C90" --append
    python3 -m generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --name "sample_dataset" -ac "King Air C90" --append
fi
KingAirC90
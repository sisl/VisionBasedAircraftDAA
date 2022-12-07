# Add '#' in front of individual lines to comment them out. The phrases preceded by '<#' begin block comments 
# and the end of the block is indicated by '#>'. Use '#' in front of the '<#' and '#>' to uncomment the 
# commands in between.

<#TESTING
python3 -m data_generation.generate_traffic_data -aw --label -ac "Cessna Skyhawk" --newac --name "test"
#>

<#CessnaSkyhawk
python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Palo Alto" --label --name "starter_dataset" -ac "Cessna Skyhawk" --newac
if ( $? ) 
{
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --label --name "starter_dataset" -ac "Cessna Skyhawk" --append
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --label --name "starter_dataset" -ac "Cessna Skyhawk" --append
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --label --name "starter_dataset" -ac "Cessna Skyhawk" --append
}
#>

<#Boeing737-800
python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Palo Alto" --label --name "starter_dataset" -ac "Boeing 737-800" --append --newac
if ( $? ) 
{
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --label --name "starter_dataset" -ac "Boeing 737-800" --append
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --label --name "starter_dataset" -ac "Boeing 737-800" --append
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --label --name "starter_dataset" -ac "Boeing 737-800" --append
}
#>

<#KingAirC90
python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Palo Alto" --label --name "starter_dataset" -ac "King Air C90" --append --newac
if ( $? ) 
{
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --label --name "starter_dataset" -ac "King Air C90" --append
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --label --name "starter_dataset" -ac "King Air C90" --append
    python -m data_generation.generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --label --name "starter_dataset" -ac "King Air C90" --append
}
#>
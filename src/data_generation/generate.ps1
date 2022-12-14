# Add '#' in front of individual lines to comment them out. The phrases preceded by '<#' begin block comments 
# and the end of the block is indicated by '#>'. Use '#' in front of the '<#' and '#>' to uncomment the 
# commands in between.

<#TESTING
python -m generate_traffic_data -aw -ac "Cessna Skyhawk" --newac --name "test"
#>

<#CessnaSkyhawk
python -m generate_traffic_data -aw --train 900 --valid 100 --location "Palo Alto" --name "sample_dataset" -ac "Cessna Skyhawk" --newac
if ( $? ) 
{
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --name "sample_dataset" -ac "Cessna Skyhawk" --append
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --name "sample_dataset" -ac "Cessna Skyhawk" --append
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --name "sample_dataset" -ac "Cessna Skyhawk" --append
}
#>

<#Boeing737-800
python -m generate_traffic_data -aw --train 9 --valid 1 --location "Palo Alto" --name "sample_dataset" -ac "Boeing 737-800" --append --newac
if ( $? ) 
{
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --name "sample_dataset" -ac "Boeing 737-800" --append
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --name "sample_dataset" -ac "Boeing 737-800" --append
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --name "sample_dataset" -ac "Boeing 737-800" --append
}
#>

<#KingAirC90
python -m generate_traffic_data -aw --train 9 --valid 1 --location "Palo Alto" --name "sample_dataset" -ac "King Air C90" --append --newac
if ( $? ) 
{
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Osh Kosh" --name "sample_dataset" -ac "King Air C90" --append
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Boston" --name "sample_dataset" -ac "King Air C90" --append
    python -m generate_traffic_data -aw --train 900 --valid 100 --location "Reno Tahoe" --name "sample_dataset" -ac "King Air C90" --append
}
#>
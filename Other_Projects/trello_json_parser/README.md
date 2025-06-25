Fork of https://gist.github.com/RealOrangeOne/c35751ee794e90df512bdfba6f22574d#file-trello-parser-py

# Trello Parser

## Download
Open a terminal, run this:

    sudo curl https://gist.githubusercontent.com/RealOrangeOne/c35751ee794e90df512bdfba6f22574d/raw/trello-parser.py -o /usr/bin/trelloparse && sudo chmod +x /usr/bin/trelloparse
    
## Usage
    $ trelloparse -h
    usage: tp [-h] input output

    positional arguments:
      input       JSON File from Trello
      output      File to output to

    optional arguments:
      -h, --help  show this help message and exit
### Example
    $ trelloparse ZRwW5Yyn.json output.json
    
## CSV
To get the output in CSV format, use https://json-csv.com/
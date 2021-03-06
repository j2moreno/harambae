"""
    All data must be compiled into a single file for upload into fixture
    Files will be concatenated into CSV format
    Also output statistics
"""


import csv
import re
import pandas as pd
import numpy as np
from collections import defaultdict


fields = [
    'Sequence',
    'BLAST',
    'Pfam',
    'Prosite',
    'KEGG Pathway',
    'NucPloc',
    'Gene Ontology',
    'Comments'
]

stats = {
    'Sequence': [0, 0],
    'BLAST': [0, 0],
    'Pfam': [0, 0],
    'Prosite': [0, 0],
    'KEGG Pathway': [0, 0],
    'NucPloc': [0, 0],
    'Gene Ontology': [0, 0],
    'Comments': [0, 0]
}

not_found = ['null', 'NULL', 'No Hits']


def concat_files():
    """
        Concatenate data files
    """
    with open('to_read.txt', 'r') as files:
        filenames = [line.strip() for line in files.readlines()]

        open('data.csv', 'w').close()

        data_df = pd.DataFrame()

        all_df = []
        for f in filenames:

            # skip these files
            if f[0] == '#':
                continue

            print(f)

            # check extension
            ext = re.findall("\S*.([ct]sv)", f)[0]
            this_df = None

            if ext == 'tsv':
                this_df = pd.read_csv(f, index_col=None, header=0, sep='\t')
            elif ext == 'csv':
                this_df = pd.read_csv(f, index_col=None, header=0)

            if this_df is not None:
                all_df.append(this_df)


        # stats calculations
        with open('statistics.tsv', 'w') as stats_out: 
            for df in all_df:
                columns = list(df.columns.values)

                # increment max value for each field
                for c in columns:
                    stats[c][1] += df.shape[0]

                for index, row in df.iterrows():
                    for c in columns:
                        if type(row[c]) == str:
                            stats[c][0] += 1
            for field in stats:
                stats_out.write(
                    '\t'.join([field] + [str(x) for x in stats[field]]) + '\n'
                )

        data_df = pd.concat(all_df, ignore_index=True)[fields]
        for item in not_found:
            data_df.replace(item, np.NaN, inplace=True)
        data_df.to_csv('data_full.csv', index=False)


def collapse_data():
    """
        Collapse multiple same-id proteins together, keeping unique keywords
        Reads every sequence and appends to a list
    """
    all_seqs = defaultdict(list)
    with open('data_full.csv', 'r') as old_data:
        old_csv = csv.reader(old_data)
        header = next(old_csv)      # header
        for record in old_csv:
            if record[0] not in all_seqs:
                all_seqs[record[0]] = [[field] for field in record[1:]]
            else:
                for index, field in enumerate(record[1:]):
                    if field not in all_seqs[record[0]][index]:
                        all_seqs[record[0]][index].append(field)

    with open('data.csv', 'w') as final:
        new_csv = csv.writer(final)
        new_csv.writerow(header)
        for sequence in all_seqs:
            new_csv.writerow([sequence] + [
                '|'.join(field) if field else '' for field in all_seqs[sequence]
            ])


if __name__ == '__main__':
    concat_files()
    collapse_data()

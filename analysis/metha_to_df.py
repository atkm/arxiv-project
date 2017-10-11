import os, gzip, glob
from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd


if __name__=='__main__':

    files = glob.glob('/home/atkm/.metha/20170923/*.xml.gz')
    #files = glob.glob('/home/atkm/.metha/20170923/2017-08-31-*.xml.gz') # test.
    arXiv_prefix = '{http://arxiv.org/OAI/arXiv/}'

    def parse_author(a):
        keyname = a.find(arXiv_prefix + "keyname")
        keyname = keyname.text if keyname is not None else ''
        forenames = a.find(arXiv_prefix + "forenames")
        forenames = forenames.text if forenames is not None else ''
        return ' '.join( (forenames, keyname) )

   
    identifier, title, authors, abstract, categories, submitted = ([] for i in range(6))
    for xmlgz in files:
        print(os.path.basename(xmlgz), end=' ')
        with gzip.open(xmlgz, 'rb') as f:
            xml = ET.parse(f)
            root = xml.getroot()
            for record in root.find('ListRecords').findall("record"):
                metadata = record.find('metadata').find(arXiv_prefix + "arXiv")
                if metadata is None:
                    continue
                
                identifier.append( metadata.find(arXiv_prefix + "id").text )
                s = metadata.find(arXiv_prefix + "created").text
                submitted.append( datetime.strptime(s, "%Y-%m-%d") )
                title.append( metadata.find(arXiv_prefix + "title").text )
                abstract.append( metadata.find(arXiv_prefix + "abstract").text.strip() )

                authors_list = metadata.find(arXiv_prefix + 'authors')
                authors.append( tuple( [parse_author(a) for a in authors_list] ) )
                
                categories_list = metadata.find(arXiv_prefix + "categories").text
                categories.append( tuple( categories_list.split() ) )
        print(' Done.')

    df = pd.DataFrame({
        'identifier': identifier,
        'title': title,
        'authors': authors,
        'abstract': abstract,
        'categories': categories,
        'submitted': submitted
        })
    print('df created.')

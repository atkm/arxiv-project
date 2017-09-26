from app import db
from models import Article

import gzip, glob
from datetime import datetime
import xml.etree.ElementTree as ET

def xml_to_sqlrow(xml):
    """
    xml: ElementTree such that xml.getroot() returns an Element
    """
    root = xml.getroot()
    arXiv_prefix = '{http://arxiv.org/OAI/arXiv/}'

    for record in root.find('ListRecords').findall("record"):        
        metadata = record.find('metadata').find(arXiv_prefix + "arXiv")
        submitted = metadata.find(arXiv_prefix + "created").text
        submitted = datetime.strptime(submitted, "%Y-%m-%d")
        authors = metadata.find(arXiv_prefix + 'authors').text
        categories = metadata.find(arXiv_prefix + "categories").text
        title = metadata.find(arXiv_prefix + "title").text
        identifier = metadata.find(arXiv_prefix + "id").text
        abstract = metadata.find(arXiv_prefix + "abstract").text.strip()

        article = Article(
                identifier = identifier,
                title = title,
                authors = authors,
                abstract = abstract,
                categories = categories,
                submitted = submitted
                )
        db.session.add(article)
                

if __name__=='__main__':
    # clear table
    # Article.query.delete()

    files = glob.glob('/home/atkm/.metha/20170923/2017-08-31-*.xml.gz') # test. Use '.metha/20170923/*.xml.gz'.

    try:
        with gzip.open(files[0], 'rb') as f:
            xml = ET.parse(f)
        xml_to_sqlrow(xml)
        db.session.commit()
        print('Population succeeded')
    except Exception as e:
        db.session.rollback()
        print(e)

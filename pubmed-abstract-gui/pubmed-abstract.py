"""
A simple example of getting article title and abstract by PMID in pubmed with gui under windows.
"""
import requests
from bs4 import BeautifulSoup
from gooey import Gooey, GooeyParser


@Gooey
def main():
    parser = GooeyParser(description="Show pubmed abstract.")
    parser.add_argument("PMID", help="PMID of the article.")
    args = parser.parse_args()

    # 发送请求, 返回请求
    response = requests.get("https://pubmed.ncbi.nlm.nih.gov/{}/".format(args.PMID))

    body = response.text

    # 解析html
    soup = BeautifulSoup(body, "html.parser")

    # find title
    print("Title:\n")
    print(soup.find(name="title").text.strip("\n"))

    # find abstract
    print("\n\nAbstract:\n")
    print(soup.find(attrs={"id": "enc-abstract"}).find(name="p").text.strip("\n"))
    return


if __name__ == "__main__":
    main()

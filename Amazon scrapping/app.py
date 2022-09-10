from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

#creating a flask app
app = Flask(__name__)

# rendering html form which we created
@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            amazon_url = "https://www.amazon.in/s?k=" + searchString
            uClient = uReq(amazon_url)
            amazonPage = uClient.read()
            uClient.close()
            amazon_html = bs(amazonPage, "html.parser")
            bigboxes = amazon_html.findAll("div", {"class": "sg-col sg-col-4-of-12 sg-col-4-of-16 sg-col-4-of-20 s-list-col-left"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.amazon.in" + box.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            #print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "a-section review aok-relative"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.find_all('div', {'class': 'a-profile-content'})[0].text
                    print(name)

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.find_all('a',{"class":"a-link-normal"})[0].text
                    print(rating)
                    # here you have to give div id
                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.find_all('a',{"class":"review-title"})[0].text
                    print(commentHead)

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.find_all('div',{"class":"a-row a-spacing-small review-data"})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].text
                    print(custComment)
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run()

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)


@app.route('/', methods=['GET'])
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            movie_url = "https://www.imdb.com/find?q="+searchString+"&ref_=nv_sr_sm"
            uClient = uReq(movie_url)
            moviePage=uClient.read()
            uClient.close()
            movie_html = bs(moviePage, "html.parser")
            final= movie_html.findAll("td", {"class": "result_text"})
            #del final[1:]
            final_link = final[0]
            movieLink = "https://www.imdb.com" + final_link.a['href']
            movieFRes = requests.get(movieLink)
            movieFRes.encoding = 'utf-8'
            movieF_html = bs(movieFRes.text, "html.parser")
            commentboxes = movieF_html.find_all('div', {'class': "user-comments"})
            allcomment=commentboxes[0].find_all('a')
            allcommentLink="https://www.imdb.com"+allcomment[len(allcomment)-1]['href']

            commentRes = requests.get(allcommentLink)
            commentRes.encoding = 'utf-8'
            comment_html = bs(commentRes.text, "html.parser")
            allc=comment_html.find_all('div', {'class':"lister-item mode-detail imdb-user-review collapsable"})

            reviews = []
            for cmt in allc:
                try:

                    name = cmt.find('span', {'class': "display-name-link"}).text

                except:
                    name = 'No Name'

                try:

                    rating = cmt.find('span', {'class': "rating-other-user-rating"}).span.text


                except:
                    rating = 'No Rating'

                try:

                    commentHead =cmt.find('div', {'class': "lister-item-content"}).a.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    cusComment = cmt.div.find('div', {'class': "content"}).div.text

                except Exception as e:
                    print("Exception while creating dictionary: ", e)

                mydict={"Movie": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                        "Comment": cusComment}
                reviews.append(mydict)
            return render_template('result.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            return render_template('error.html')

    else:
        return render_template('index.html')

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=True)

from YelpAPI import yelp
from bs4 import BeautifulSoup
import requests
import time

#get url and review_count through Yelp API
connection = yelp('new-york-sports-club-new-york')
url = connection.get_url()
num_reviews = connection.get_review_number()

#trim url 
def trim_url(raw_url, sort_by = None):
	#no question mark in url
	if raw_url.find('?') == -1:
		return raw_url

	questionMarkPos = [i for i in range(len(raw_url)) if raw_url[i] == '?']
	for pos in questionMarkPos:
		test_url = raw_url[:(pos + 1)]
		try:
			_ = requests.get(test_url)
			break
		except:
			#protect from being blocked
			time.sleep(1)
			continue

	sort_map = {'newest':'date_desc', 'oldest':'date_asc', 'highest':'rating_desc',
		'lowest':'rating_asc', 'elites':'elites_desc'}
	if sort_by:
		try:
			append = sort_map[sort_by]
			return  '{}sort_by={}'.format(test_url, append)
		except KeyError as err:
			print 'Unrecognized value', err
	return test_url

def get_html(url, trim = True):
	#grab the page
	if trim:
		url = trim_url(url, 'newest')
	r = requests.get(url)
	assert r.status_code == 200
	return r.text, url


#grap all the comments
comments = []
count = 0

while count < num_reviews:
    #only trim the url when scrappin the first page
    if count == 0:
        html, trimed_url = get_html(url)
    else:
        html, _ = get_html(page_url, trim=False)
    soup = BeautifulSoup(html, 'html.parser')
    page_comment = soup.findAll('p', lang = 'en')
    for i in page_comment:
        comments.append(i.text)
    #next page
    #anti-block sleeping
    time.sleep(1)
    count += 20
    page_url = '{}&start={}'.format(trimed_url, count)

#clean up /xa0 in comments
print 'There are total {} comments'.format(len(comments))
def clean_space(comment):
    return comment.replace(u'\xa0', u' ')
comments = map(clean_space, comments)


#topic modeling
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

n_topics = 5
n_top_words = 15
n_features = 1000

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()
    
tf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
                               max_features = n_features,
                               stop_words = 'english')
tf = tf_vectorizer.fit_transform(comments)
tf_feature_names = tf_vectorizer.get_feature_names()
lda = LatentDirichletAllocation(n_topics=n_topics, max_iter = 10,
                               learning_method = 'batch',random_state =0)
lda.fit(tf)
#print lda.perplexity(tf)
print_top_words(lda, tf_feature_names, n_top_words)
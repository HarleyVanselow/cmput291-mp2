from bsddb3 import db
def main():
	termdatabase = db.DB()
	termdatabase.open("../phase2/te.idx")
	datedatabase = db.DB()
	datedatabase.open("../phase2/da.idx")
	tweetdatabase = db.DB()
	tweetdatabase.open("../phase2/tw.idx")
	
	databases = {"terms":termdatabase,"tweets":tweetdatabase,"dates":datedatabase}
	while(1):
		query = input()
		if(query == 'exit'):
			break
		run_query(query,databases)
	
	for key,value in databases.items(): value.close()


def run_query(query,databases):
	#Doesn't really work yet but its a start
	print(databases["terms"].cursor().get(bytes(query,'utf-8'),db.DB_FIRST))
	


if __name__ == "__main__":
	main()

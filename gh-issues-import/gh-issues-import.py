import urllib2
import json
from StringIO import StringIO
import base64
import sys

#==== configurations =======
username = "doutriaux1@llnl.gov"
password = "g1thub1"
src_repo = "UV-CDAT/uvcdat"
dst_repo = "doutriaux1/uvcdat-1"
dst_repo = "UV-CDAT/uvcdat-devel"
#==== end of configurations ===

server = "api.github.com"
src_url = "https://%s/repos/%s" % (server, src_repo)
dst_url = "https://%s/repos/%s" % (server, dst_repo)

print dst_url
def get_milestones(url):
	response = urllib2.urlopen("%s/milestones?state=open" % url)
	result = response.read()
	milestones = json.load(StringIO(result))
	return milestones

def get_labels(url):
	response = urllib2.urlopen("%s/labels" % url)
	result = response.read()
	labels = json.load(StringIO(result))
	return labels

def get_issues(url):
	response = urllib2.urlopen("%s/issues" % url)
	result = response.read()
	issues = json.load(StringIO(result))
	return issues

def get_comments_on_issue(issue):
	if issue.has_key("comments") \
	  and issue["comments"] is not None \
	  and issue["comments"] != 0:
		response = urllib2.urlopen("%s/comments" % issue["url"])
		result = response.read()
		comments = json.load(StringIO(result))
		return comments
	else :
		return []

def import_milestones(milestones):
	for source in milestones:
		dest = json.dumps({
			"title": source["title"],
			"state": "open",
			"description": source["description"],
			"due_on": source["due_on"]})

		req = urllib2.Request("%s/milestones" % dst_url, dest)
		req.add_header("Authorization", "Basic " + base64.urlsafe_b64encode("%s:%s" % (username, password)))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		res = urllib2.urlopen(req)
		
		data = res.read()
		res_milestone = json.load(StringIO(data))
		print "Successfully created milestone %s" % res_milestone["title"]

def import_labels(labels):
	for source in labels:
		dest = json.dumps({
			"name": source["name"],
			"color": source["color"]
		})

		req = urllib2.Request("%s/labels" % dst_url, dest)
		req.add_header("Authorization", "Basic " + base64.urlsafe_b64encode("%s:%s" % (username, password)))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		print "Request:",dst_url,req
		res = urllib2.urlopen(req)

		data = res.read()
		res_label = json.load(StringIO(data))
		print "Successfully created label %s" % res_label["name"]

def import_issues(issues, dst_milestones, dst_labels):
	for source in issues:
		labels = []
		if source.has_key("labels"):
			for src_label in source["labels"]:
				name = src_label["name"]
				for dst_label in dst_labels:
					if dst_label["name"] == name:
						labels.append(name)
						break

		milestone = None
		if source.has_key("milestone") and source["milestone"] is not None:
			title = source["milestone"]["title"]
			for dst_milestone in dst_milestones:
				if dst_milestone["title"] == title:
					milestone = dst_milestone["number"]
					break

		assignee = None
		if source.has_key("assignee") and source["assignee"] is not None:
			assignee = source["assignee"]["login"]

		body = None
		if source.has_key("body") and source["body"] is not None:
			body = source["body"]

		dest = json.dumps({
			"title": source["title"],
		    "body": body,
		    "assignee": assignee,
		    "milestone": milestone,
		    "labels": labels
		})

		comments = get_comments_on_issue(source)
		print "Comments",comments
		#todo: insert logic on comments if needed

		req = urllib2.Request("%s/issues" % dst_url, dest)
		req.add_header("Authorization", "Basic " + base64.urlsafe_b64encode("%s:%s" % (username, password)))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		res = urllib2.urlopen(req)

		data = res.read()
		res_issue = json.load(StringIO(data))
		print "Successfully created issue %s" % source["title"]
		
def export_issues(issues):
	for source in issues[:1]:
		#print "desT:",dest
		comments = get_comments_on_issue(source)
		print "Comments:",comments
		if source.has_key("comments"):
			del(source["comments"])
		#todo: insert logic on comments if needed
		dest = json.dumps(source)

		req = urllib2.Request("%s/issues" % dst_url, dest)
		req.add_header("Authorization", "Basic " + base64.urlsafe_b64encode("%s:%s" % (username, password)))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		res = urllib2.urlopen(req)

		data = res.read()
		res_issue = json.load(StringIO(data))
		print "Successfully created issue %s" % source["title"]

def trim(src,dst,uniqueKey=u'title',check_all=False):
	out = []
	up = []
	for s in src:
		keep = True
		keep2 = False
		for d in dst:
			if s[uniqueKey]==d[uniqueKey]:
				keep = False
				if check_all:
					for k in s:
						if s[k]!=d[k]:
							keep2 = True
							break
		if keep:
			out.append(s)
		if keep2:
			up.append(s)
	if check_all:
		return out,up
	else:
		return out

def main(fromFile=True):
	if fromFile:
		f=open("res.asc")
		milestones = eval(f.readline())
		milestones2 = eval(f.readline())
		labels = eval(f.readline())
		labels2 = eval(f.readline())
		issues = eval(f.readline())
		issues2 = eval(f.readline())
	else:
		f = open("res.asc","w")
		#get milestones and issues to import
		milestones = get_milestones(src_url)
		milestones2 = get_milestones(dst_url)
		print >> f,repr(milestones)
		print >> f,repr(milestones2)
		labels = get_labels(src_url)
		labels2 = get_labels(dst_url)
		print >> f, repr(labels)
		print >> f, repr(labels2)
		issues = get_issues(src_url)
		issues2 = get_issues(dst_url)
		print >> f, repr(issues)
		print >> f, repr(issues2)
		#print issues[0].keys()
		f.close()

	print "original milestones:",milestones
	milestones = trim(milestones,milestones2)
	print "New milestones:",milestones
	labels = trim(labels,labels2,u'name')
	print "New labels",labels
	#do import
	import_milestones(milestones)
	import_labels(labels)

	#get imported milestones and labels
	#milestones = get_milestones(dst_url)
	#labels = get_labels(dst_url)

	#process issues
	issues,updated_issues = trim(issues,issues2,check_all=True)
	print "New issues:",issues
	print "updated issues:",updated_issues
	export_issues(updated_issues[::-1])

if __name__ == '__main__':
	main(fromFile=True)


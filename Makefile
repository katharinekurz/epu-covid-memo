PUBLISH_REMOTE ?= origin
PUBlISH_BRANCH ?= master
ENTRYPOINT     := countydata.py

.PHONY: generate

deps:
	pip3 install -r requirements.txt

clean:
	rm -rf data headfile.xls

generate: clean
	python3 countydata.py

publish:
	python3 scripts/publish.py

update: generate publish
	git add .
	git commit -m "update covid dataset"
	git push $(PUBLISH_REMOTE) $(PUBLISH_BRANCH)

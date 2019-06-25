.DEFAULT_GOAL := deploy

export GITHUB_ORG  ?= akranga
export APPLICATION ?= kfp-app1

install uninstall clean elaborate:
	$(MAKE) -C .hub $@

.PHONY: deploy undeploy

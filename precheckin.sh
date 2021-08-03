#!/bin/sh

# This script is based on libcdio_spec-prepare.sh (thanks to sbrabec@suse.cz)
# create a -mini spec for systemd for bootstrapping

ORIG_SPEC=systemd
EDIT_WARNING="##### WARNING: please do not edit this auto generated spec file. Use the ${ORIG_SPEC}.spec! #####\n"
sed "s/^%bcond_with     systemd_bootstrap.*$/${EDIT_WARNING}%bcond_without     systemd_bootstrap/;
     s/^Name:.*/&-mini/
	      " < ${ORIG_SPEC}.spec > ${ORIG_SPEC}-mini.spec
#cp ${ORIG_SPEC}.changes ${ORIG_SPEC}-mini.changes
cp ${ORIG_SPEC}-rpmlintrc ${ORIG_SPEC}-mini-rpmlintrc

osc service localrun format_spec_file

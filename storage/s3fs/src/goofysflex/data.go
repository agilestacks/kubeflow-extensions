package main

import "os/user"

// MountOptions structure encapsulates config options
type MountOptions struct {
	Bucket         string `json:"bucket,omitempty"`
	SubPath        string `json:"sub-path,omitempty"`
	Region         string `json:"region,omitempty"`
	Endpoint       string `json:"endpoint,omitempty"`
	DirMode        string `json:"dir-mode,omitempty"`
	FileMode       string `json:"file-mode,omitempty"`
	GID            string `json:"gid,omitempty"`
	UID            string `json:"uid,omitempty"`
	ACL            string `json:"acl,omitempty"`
	AccessKeyB64   string `json:"kubernetes.io/secret/accesskey,omitempty"`
	SecretKeyB64   string `json:"kubernetes.io/secret/secretkey,omitempty"`
	PVName         string `json:"kubernetes.io/pvOrVolumeName,omitempty"`
	ServiceAccount string `json:"kubernetes.io/serviceAccount.name,omitempty"`
}

// Response is a canonical form of flex drive response
type Response struct {
	Status     string `json:"status,omitempty"`
	Message    string `json:"message,omitempty"`
	Device     string `json:"device,omitempty"`
	VolumeName string `json:"volumeName,omitempty"`
	Attached   bool   `json:"attached,omitempty"`
}

// DefaultMountOptions returns default values for MountOptions
func DefaultMountOptions() MountOptions {
	user, _ := user.Current()
	return MountOptions{
		Region:   "us-east-1",
		DirMode:  "0755",
		FileMode: "0644",
		GID:      user.Gid,
		UID:      user.Uid,
		ACL:      "private",
	}
}

// respondInit creates a custom response because
// of nested structure "capabilities" needed only in one place
func respondInit(attach bool) {
	resp := struct {
		Status string `json:"status"`
		Cap    struct {
			Attach bool `json:"attach"`
		} `json:"capabilities,omitempty"`
	}{
		Status: "Success",
		Cap: struct {
			Attach bool `json:"attach"`
		}{
			Attach: attach,
		},
	}
	printJSON(resp)
}

// respondError predefined response for frequent use
func respondError(err error) {
	resp := Response{
		Status:  "Failure",
		Message: err.Error(),
	}
	printJSON(resp)
}

// respondSuccess predefined response for frequent use
func respondSuccess() {
	resp := Response{
		Status: "Success",
	}
	printJSON(resp)
}

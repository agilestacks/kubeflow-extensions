// Flex plugin data contract https://docs.okd.io/latest/install_config/persistent_storage/persistent_storage_flex_volume.html
package main

import (
	"encoding/json"
	"errors"

	"github.com/sirupsen/logrus"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:           app,
	Short:         "enables goofys support for kubernetes",
	Long:          `This is a flex plugin for Kubernetes to enable goofys support for kubernetes'`,
	SilenceUsage:  false,
	SilenceErrors: true,
}

var mountCmd = &cobra.Command{
	Use:           "mount MOUNTDIR JSON",
	Short:         "reacts on mount action",
	Long:          `Executed by kubelet. This is a CLI callback to react on mount volume operation'`,
	RunE:          runMount,
	SilenceUsage:  true,
	SilenceErrors: true,
}

var unmountCmd = &cobra.Command{
	Use:           "unmount MOUNTDIR",
	Short:         "reacts on unmount action",
	Long:          `Executed by kubelet. This is a CLI callback to react on unmount volume operation'`,
	RunE:          runUnmount,
	SilenceUsage:  true,
	SilenceErrors: true,
}

var initCmd = &cobra.Command{
	Use:           "init JSON",
	Short:         "reacts on init action",
	Long:          `Executed by kubelet. At present does nothing`,
	Run:           runInit,
	SilenceUsage:  true,
	SilenceErrors: true,
}

func runInit(c *cobra.Command, args []string) {
	respondInit(false)
}

func runDefaultResponse(c *cobra.Command, args []string) {
	respondSuccess()
}

func runMount(c *cobra.Command, args []string) error {
	if len(args) < 2 {
		return errors.New("expecting at least 2 arguments: MOUNTDIR JSON")
	}

	target := args[0]
	optsS := args[1]

	if optsS == "" {
		return errors.New("Mount options in JSON format expected")
	}

	logrus.Infof("Mount %s using %s", target, optsS)

	opts, err := UnmarshalMountOpts(optsS)
	if err != nil {
		logrus.Errorf("Error %s to decode JSON: %s", err, optsS)
	}
	return Mount(target, opts)
}

func runUnmount(c *cobra.Command, args []string) error {
	if len(args) == 0 {
		return errors.New("Unmount must have at least 1 argument")
	}

	target := args[0]
	logrus.Infof("Unmount %s", target)

	return Unmount(target)
}

// UnmarshalMountOpts constructs MountOptions from json payload
func UnmarshalMountOpts(s string) (MountOptions, error) {
	opts := DefaultMountOptions()
	err := json.Unmarshal([]byte(s), &opts)
	if err != nil {
		logrus.Errorf("Error %s to decode JSON: %s", err, s)
	}
	return opts, err
}

func init() {
	rootCmd.AddCommand(mountCmd)
	rootCmd.AddCommand(unmountCmd)
	rootCmd.AddCommand(initCmd)
}

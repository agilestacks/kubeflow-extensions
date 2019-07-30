package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/yunabe/easycsv"
)

type Entry struct {
	Name string `index:"0"`
	Age  int64  `index:"1"`
}

func main() {
    fmt.Printf(`CSV.go arguments: %s`, os.Args)
	if len(os.Args) != 3 {
		usage()
	}

	in := open(os.Args[1], os.O_RDONLY)
	out := open(os.Args[2], os.O_WRONLY|os.O_CREATE|os.O_TRUNC)

	r := easycsv.NewReadCloser(in)
	var entry Entry
	for r.Read(&entry) {
		fmt.Fprintf(out, "%s,%f\n", strings.ToUpper(entry.Name), float64(entry.Age)/2.0)
	}
	out.Close()
	if err := r.Done(); err != nil {
		log.Fatalf("Failed to read: %v", err)
	}
}

func open(filename string, mode int) *os.File {
	if filename == "-" {
		if mode&os.O_WRONLY != 0 {
			return os.Stdout
		}
		return os.Stdin
	}
	file, err := os.OpenFile(filename, mode, 0664)
	if err != nil {
		log.Fatalf("Unable to open `%s`: %v", filename, err)
	}
	return file
}

func usage() {
	fmt.Printf(`Usage:
	%s input.csv output.csv
Use - (dash) in place of filename to read from stdin and/or write to stdout
`, os.Args[0])
	os.Exit(2)
}

package main

import (
	"embed"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"time"

	"rapid-message-sender/pkg/api"
	"rapid-message-sender/pkg/version"
)

//go:embed frontend/*
var frontendFS embed.FS

func main() {
	server := api.NewServer(frontendFS)
	defer server.Close()

	shutdownCh := make(chan struct{})
	server.SetOnShutdown(func() {
		close(shutdownCh)
	})

	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		fmt.Printf("Failed to bind local listener: %v\n", err)
		os.Exit(1)
	}

	port := listener.Addr().(*net.TCPAddr).Port
	appURL := fmt.Sprintf("http://127.0.0.1:%d", port)

	mux := server.SetupRoutes()

	httpServer := &http.Server{
		Handler: mux,
	}

	go func() {
		if err := httpServer.Serve(listener); err != nil && err != http.ErrServerClosed {
			fmt.Printf("HTTP server error: %v\n", err)
		}
	}()

	go launchDesktopWindow(appURL)

	// Block until shutdown signal is received
	<-shutdownCh
	fmt.Println("[Main] Shutting down backend process...")
	httpServer.Close()
	time.Sleep(100 * time.Millisecond)
	os.Exit(0)
}

func launchDesktopWindow(appURL string) {
	time.Sleep(150 * time.Millisecond)

	userDataDir := filepath.Join(os.Getenv("LOCALAPPDATA"), "RapidMessageSender", "UserData")

	switch runtime.GOOS {
	case "windows":
		edgePaths := []string{
			os.Getenv("ProgramFiles(x86)") + `\Microsoft\Edge\Application\msedge.exe`,
			os.Getenv("ProgramFiles") + `\Microsoft\Edge\Application\msedge.exe`,
			"msedge.exe",
		}

		for _, path := range edgePaths {
			if _, err := os.Stat(path); err == nil || path == "msedge.exe" {
				cmd := exec.Command(path, fmt.Sprintf("--app=%s", appURL), fmt.Sprintf("--user-data-dir=%s", userDataDir), "--window-size=1200,850")
				if err := cmd.Start(); err == nil {
					return
				}
			}
		}

		chromePaths := []string{
			os.Getenv("ProgramFiles(x86)") + `\Google\Chrome\Application\chrome.exe`,
			os.Getenv("ProgramFiles") + `\Google\Chrome\Application\chrome.exe`,
			"chrome.exe",
		}
		for _, path := range chromePaths {
			cmd := exec.Command(path, fmt.Sprintf("--app=%s", appURL), fmt.Sprintf("--user-data-dir=%s", userDataDir), "--window-size=1200,850")
			if err := cmd.Start(); err == nil {
				return
			}
		}

		exec.Command("rundll32", "url.dll,FileProtocolHandler", appURL).Start()

	case "linux":
		cmd := exec.Command("google-chrome", fmt.Sprintf("--app=%s", appURL), fmt.Sprintf("--user-data-dir=%s", userDataDir), "--window-size=1200,850")
		if err := cmd.Start(); err != nil {
			exec.Command("xdg-open", appURL).Start()
		}

	case "darwin":
		cmd := exec.Command("open", "-na", "Google Chrome", "--args", fmt.Sprintf("--app=%s", appURL), fmt.Sprintf("--user-data-dir=%s", userDataDir), "--window-size=1200,850")
		if err := cmd.Start(); err != nil {
			exec.Command("open", appURL).Start()
		}
	}
}

func getVersion() string {
	return version.AppVersion
}
package net

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"rapid-message-sender/pkg/version"
)

type ReleaseInfo struct {
	TagName       string `json:"tag_name"`
	Name          string `json:"name"`
	Body          string `json:"body"`
	HtmlUrl       string `json:"html_url"`
	PublishedAt   string `json:"published_at"`
	CurrentVer    string `json:"current_version"`
	LatestVer     string `json:"latest_version"`
	HasUpdate     bool   `json:"has_update"`
	CurrentSHA256 string `json:"current_sha256"`
	LatestSHA256  string `json:"latest_sha256"`
	SHAMatch      bool   `json:"sha_match"`
}

type GitHubAsset struct {
	Name               string `json:"name"`
	Size               int64  `json:"size"`
	BrowserDownloadURL string `json:"browser_download_url"`
}

type GitHubRelease struct {
	TagName     string        `json:"tag_name"`
	Name        string        `json:"name"`
	Body        string        `json:"body"`
	HtmlUrl     string        `json:"html_url"`
	PublishedAt string        `json:"published_at"`
	Assets      []GitHubAsset `json:"assets"`
}

// Calculate SHA256 of current running executable
func getRunningBinarySHA256() string {
	execPath, err := os.Executable()
	if err != nil {
		return ""
	}
	file, err := os.Open(execPath)
	if err != nil {
		return ""
	}
	defer file.Close()

	hasher := sha256.New()
	if _, err := io.Copy(hasher, file); err != nil {
		return ""
	}
	return fmt.Sprintf("%x", hasher.Sum(nil))
}

// CheckUpdate checks GitHub releases API for newer version and matches SHA256 hashes.
func CheckUpdate() (ReleaseInfo, error) {
	currentSHA := getRunningBinarySHA256()
	client := &http.Client{Timeout: 5 * time.Second}
	url := "https://api.github.com/repos/showayebDev/Rapid_Message_Sender/releases/latest"

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return ReleaseInfo{
			CurrentVer:    version.AppVersion,
			LatestVer:     version.AppVersion,
			HasUpdate:     false,
			CurrentSHA256: currentSHA,
			SHAMatch:      true,
		}, nil
	}
	req.Header.Set("User-Agent", "RapidMessageSender-App")

	resp, err := client.Do(req)
	if err != nil {
		return ReleaseInfo{
			CurrentVer:    version.AppVersion,
			LatestVer:     version.AppVersion,
			HasUpdate:     false,
			CurrentSHA256: currentSHA,
			SHAMatch:      true,
		}, nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return ReleaseInfo{
			CurrentVer:    version.AppVersion,
			LatestVer:     version.AppVersion,
			HasUpdate:     false,
			CurrentSHA256: currentSHA,
			SHAMatch:      true,
		}, nil
	}

	var ghRelease GitHubRelease
	if err := json.NewDecoder(resp.Body).Decode(&ghRelease); err != nil {
		return ReleaseInfo{
			CurrentVer:    version.AppVersion,
			LatestVer:     version.AppVersion,
			HasUpdate:     false,
			CurrentSHA256: currentSHA,
			SHAMatch:      true,
		}, nil
	}

	latestSHA := ""

	// Check assets for SHA256SUMS or checksum text files
	for _, asset := range ghRelease.Assets {
		lowerName := strings.ToLower(asset.Name)
		if strings.Contains(lowerName, "sha256") || strings.Contains(lowerName, "checksum") {
			assetReq, err := http.NewRequest("GET", asset.BrowserDownloadURL, nil)
			if err == nil {
				assetReq.Header.Set("User-Agent", "RapidMessageSender-App")
				if assetResp, err := client.Do(assetReq); err == nil {
					bodyBytes, err := io.ReadAll(assetResp.Body)
					assetResp.Body.Close()
					if err == nil {
						content := string(bodyBytes)
						execPath, _ := os.Executable()
						execName := strings.ToLower(filepath.Base(execPath))
						for _, line := range strings.Split(content, "\n") {
							lineLower := strings.ToLower(line)
							if strings.Contains(lineLower, execName) || strings.Contains(lineLower, "rapidmessagesender") {
								fields := strings.Fields(line)
								for _, f := range fields {
									cleanF := strings.Trim(f, "`\":;,()")
									if len(cleanF) == 64 {
										latestSHA = strings.ToLower(cleanF)
										break
									}
								}
							}
						}
					}
				}
			}
		}
	}

	// Fallback to body parsing if not found in assets
	if latestSHA == "" {
		for _, line := range strings.Split(ghRelease.Body, "\n") {
			lineLower := strings.ToLower(line)
			if strings.Contains(lineLower, "sha256") || strings.Contains(lineLower, "sha-256") {
				for _, part := range strings.Fields(line) {
					cleanPart := strings.Trim(part, "`\":;,()")
					if len(cleanPart) == 64 {
						latestSHA = strings.ToLower(cleanPart)
						break
					}
				}
			}
		}
	}

	shaMatch := true
	if latestSHA != "" && currentSHA != "" {
		shaMatch = (latestSHA == currentSHA)
	}

	hasUpdate := false
	// Trigger update if version tag differs OR if version matches but SHA256 does NOT match
	if ghRelease.TagName != "" && ghRelease.TagName != version.AppVersion {
		hasUpdate = true
	} else if !shaMatch {
		hasUpdate = true
	}

	return ReleaseInfo{
		TagName:       ghRelease.TagName,
		Name:          ghRelease.Name,
		Body:          ghRelease.Body,
		HtmlUrl:       ghRelease.HtmlUrl,
		PublishedAt:   ghRelease.PublishedAt,
		CurrentVer:    version.AppVersion,
		LatestVer:     ghRelease.TagName,
		HasUpdate:     hasUpdate,
		CurrentSHA256: currentSHA,
		LatestSHA256:  latestSHA,
		SHAMatch:      shaMatch,
	}, nil
}

package controllers

import (
	"log"
	"os/exec"

	"github.com/gin-gonic/gin"
)

// RunCleanup triggers the Python cleanup script
func RunCleanup(c *gin.Context) {
	cmd := exec.Command("python3", "Tasks/cleanup.py")

	// Capture script output
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Error executing cleanup.py: %v", err)
		c.JSON(500, gin.H{"error": "Failed to execute cleanup script", "details": err.Error()})
		return
	}

	// Send script output as response
	c.JSON(200, gin.H{"message": "Cleanup completed", "output": string(output)})
}

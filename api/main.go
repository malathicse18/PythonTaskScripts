package main

import (
	"PYTHONTASKS/api/routes"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	// Register routes
	routes.SetupCleanupRoutes(router)

	// Start the server
	router.Run(":8080") // Running on port 8080
}

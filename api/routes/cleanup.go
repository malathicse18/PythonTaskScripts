package routes

import (
	"PYTHONTASKS/api/controllers"

	"github.com/gin-gonic/gin"
)

// SetupCleanupRoutes registers cleanup-related API endpoints
func SetupCleanupRoutes(router *gin.Engine) {
	router.POST("/cleanup", controllers.RunCleanup)
}

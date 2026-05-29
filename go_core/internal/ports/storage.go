package ports

import (
	"context"
	"io"
	"time"
)

type IStorageAdapter interface {
	UploadObject(ctx context.Context, bucketName string, objectName string, reader io.Reader, objectSize int64, contentType string) error
	GetPresignedURL(ctx context.Context, bucketName string, objectName string, expires time.Duration) (string, error)
}

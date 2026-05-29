package storage

import (
	"context"
	"io"
	"net/url"
	"time"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

type MinIOAdapter struct {
	client *minio.Client
}

func NewMinIOAdapter(endpoint, accessKey, secretKey string, useSSL bool) (*MinIOAdapter, error) {
	client, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
		Secure: useSSL,
	})
	if err != nil {
		return nil, err
	}

	return &MinIOAdapter{client: client}, nil
}

func (a *MinIOAdapter) UploadObject(ctx context.Context, bucketName string, objectName string, reader io.Reader, objectSize int64, contentType string) error {
	// Ensure bucket exists
	exists, err := a.client.BucketExists(ctx, bucketName)
	if err != nil {
		return err
	}
	if !exists {
		err = a.client.MakeBucket(ctx, bucketName, minio.MakeBucketOptions{})
		if err != nil {
			return err
		}
	}

	_, err = a.client.PutObject(ctx, bucketName, objectName, reader, objectSize, minio.PutObjectOptions{
		ContentType: contentType,
	})
	return err
}

func (a *MinIOAdapter) GetPresignedURL(ctx context.Context, bucketName string, objectName string, expires time.Duration) (string, error) {
	reqParams := make(url.Values)
	presignedURL, err := a.client.PresignedGetObject(ctx, bucketName, objectName, expires, reqParams)
	if err != nil {
		return "", err
	}
	return presignedURL.String(), nil
}

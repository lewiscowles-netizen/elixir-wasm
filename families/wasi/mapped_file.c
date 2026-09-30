// Heap-backed file loader for the WASI capability filesystem.
#include "mapped_file.h"
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

MappedFile *mapped_file_open_beam(const char *name)
{
    int fd = open(name, O_RDONLY);
    if (fd < 0) {
        perror(name);
        return NULL;
    }
    struct stat info;
    if (fstat(fd, &info) || info.st_size < 12 || (uint64_t) info.st_size > UINT32_MAX) {
        close(fd);
        return NULL;
    }
    MappedFile *file = calloc(1, sizeof(*file));
    if (!file) {
        close(fd);
        return NULL;
    }
    file->fd = fd;
    file->size = info.st_size;
    file->mapped = malloc(file->size);
    if (!file->mapped) {
        mapped_file_close(file);
        return NULL;
    }
    size_t offset = 0;
    while (offset < file->size) {
        ssize_t count = read(fd, (char *) file->mapped + offset, file->size - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            mapped_file_close(file);
            return NULL;
        }
        offset += count;
    }
    return file;
}

void mapped_file_close(MappedFile *file)
{
    free(file->mapped);
    close(file->fd);
    free(file);
}

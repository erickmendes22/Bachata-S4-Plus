// Native client for Bachata Android 0.2.7 SafBrokerSession (BSF1).
// Big-endian DataInputStream/DataOutputStream. OP_OPEN transfers SCM_RIGHTS.
#include "android_saf_transport.h"
#include <cerrno>
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

namespace BachataSaf::Protocol {
namespace {
constexpr std::uint32_t Magic = 0x42534631;
constexpr unsigned MaxPayload = 8 * 1024 * 1024;
void Put16(std::vector<std::uint8_t>& b, unsigned n) {
    b.push_back(std::uint8_t(n >> 8)); b.push_back(std::uint8_t(n));
}
void Put32(std::vector<std::uint8_t>& b, std::uint32_t n) {
    b.push_back(std::uint8_t(n >> 24)); b.push_back(std::uint8_t(n >> 16));
    b.push_back(std::uint8_t(n >> 8)); b.push_back(std::uint8_t(n));
}
bool SendAll(int fd, const std::uint8_t* p, std::size_t n) {
    while(n) {
        const ssize_t r = send(fd,p,n,MSG_NOSIGNAL);
        if (r < 0 && errno == EINTR) continue;
        if (r <= 0) return false;
        p += r; n -= r;
    }
    return true;
}
bool RecvAll(int fd, std::uint8_t* p, std::size_t n) {
    while(n) {
        const ssize_t r = recv(fd,p,n,0);
        if (r < 0 && errno == EINTR) continue;
        if (r <= 0) return false;
        p += r; n -= r;
    }
    return true;
}
}
std::uint16_t Read16(const std::uint8_t* p) { return (std::uint16_t(p[0])<<8)|p[1]; }
std::uint32_t Read32(const std::uint8_t* p) {
    return (std::uint32_t(p[0])<<24)|(std::uint32_t(p[1])<<16)|
           (std::uint32_t(p[2])<<8)|p[3];
}
std::uint64_t Read64(const std::uint8_t* p) {
    return (std::uint64_t(Read32(p))<<32)|Read32(p+4);
}
Reply Request(const std::string& socket_name, const std::string& token,
              int operation, std::string_view relative) {
    Reply reply;
    if (socket_name.empty() || socket_name.size() >= sizeof(sockaddr_un::sun_path) ||
        token.empty() || token.size()>128 || relative.size()>4096 ||
        operation<1 || operation>3) return reply;
    const int sk = socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);
    if (sk<0) return reply;
    timeval timeout{5,0};
    (void)setsockopt(sk,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout));
    (void)setsockopt(sk,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout));
    sockaddr_un addr{};
    addr.sun_family=AF_UNIX;
    addr.sun_path[0]='\0';
    std::memcpy(addr.sun_path+1,socket_name.data(),socket_name.size());
    if(connect(sk,reinterpret_cast<const sockaddr*>(&addr),
               socklen_t(offsetof(sockaddr_un,sun_path)+1+socket_name.size()))!=0) {
        std::fprintf(stderr,"BIONIC_SAF_CONNECT_FAILED errno=%d\n",errno);
        close(sk); return reply;
    }
    std::vector<std::uint8_t> req;
    req.reserve(12+token.size()+relative.size());
    Put32(req,Magic); req.push_back(1); req.push_back(std::uint8_t(operation));
    Put16(req,unsigned(token.size())); Put32(req,unsigned(relative.size()));
    req.insert(req.end(),token.begin(),token.end());
    req.insert(req.end(),relative.begin(),relative.end());
    if(!SendAll(sk,req.data(),req.size())) { close(sk); return reply; }
    // Ancillary descriptor accompanies the FIRST write of Java's header,
    // so recvmsg is required for the first bytes, not a separate recv().
    std::uint8_t head[10]{};
    iovec iov{head,sizeof(head)};
    alignas(cmsghdr) char ancillary[CMSG_SPACE(sizeof(int)*4)]{};
    msghdr msg{};
    msg.msg_iov=&iov; msg.msg_iovlen=1;
    msg.msg_control=ancillary; msg.msg_controllen=sizeof(ancillary);
    ssize_t got;
    do { got=recvmsg(sk,&msg,MSG_CMSG_CLOEXEC); }
    while(got<0 && errno==EINTR);
    if(got<=0 || (msg.msg_flags&MSG_CTRUNC)) { close(sk); return reply; }
    for(cmsghdr* c=CMSG_FIRSTHDR(&msg);c;c=CMSG_NXTHDR(&msg,c)) {
        if(c->cmsg_level!=SOL_SOCKET || c->cmsg_type!=SCM_RIGHTS ||
           c->cmsg_len<CMSG_LEN(sizeof(int))) continue;
        const auto* fds=reinterpret_cast<const int*>(CMSG_DATA(c));
        const std::size_t n=(c->cmsg_len-CMSG_LEN(0))/sizeof(int);
        for(std::size_t i=0;i<n;i++) {
            if(reply.fd<0) reply.fd=fds[i];
            else close(fds[i]);
        }
    }
    if(std::size_t(got)<sizeof(head) &&
       !RecvAll(sk,head+got,sizeof(head)-std::size_t(got))) {
        if(reply.fd>=0)close(reply.fd);
        reply.fd=-1; close(sk);return reply;
    }
    const std::size_t size=Read32(head+6);
    if(Read32(head)!=Magic || head[4]!=1 || size>MaxPayload) {
        if(reply.fd>=0)close(reply.fd);
        reply.fd=-1;close(sk);return reply;
    }
    reply.status=head[5];
    reply.bytes.resize(size);
    if(size && !RecvAll(sk,reply.bytes.data(),size)) reply.status=-1;
    close(sk);
    if(reply.status!=0 && reply.fd>=0) {
        close(reply.fd); reply.fd=-1;
    }
    return reply;
}
}

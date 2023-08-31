#ifndef EXPLICIT_INSTANTIATIONS_H
#define EXPLICIT_INSTANTIATIONS_H

#include <string>
#include <vector>


#define VIS __attribute__((visibility("default")))

#define INSTANT_EQ(DEF, T, ...) \
  DEF template VIS bool operator==(const T<__VA_ARGS__>&, const T<__VA_ARGS__>&); \
  DEF template VIS bool operator!=(const T<__VA_ARGS__>&, const T<__VA_ARGS__>&)

#define INSTANT_CMP(DEF, T, ...) \
    DEF template VIS bool operator==(const T<__VA_ARGS__>&, const T<__VA_ARGS__>&); \
    DEF template VIS bool operator!=(const T<__VA_ARGS__>&, const T<__VA_ARGS__>&); \
    DEF template VIS bool operator<(const T<__VA_ARGS__>&, const T<__VA_ARGS__>&); \
    DEF template VIS bool operator<=(const T<__VA_ARGS__>&, const T<__VA_ARGS__>&); \
    DEF template VIS bool operator>(const T<__VA_ARGS__>&, const T<__VA_ARGS__>&); \
    DEF template VIS bool operator>=(const T<__VA_ARGS__>&, const T<__VA_ARGS__>&)

#define INSTANTIATE_ITERATORS(DEF, ...) \
    DEF template class VIS ForwardIterator<__VA_ARGS__>; \
    DEF template class VIS InputIterator<__VA_ARGS__>; \
    DEF template class VIS BidirectionalIterator<__VA_ARGS__>; \
    DEF template class VIS RandomAccessIterator<__VA_ARGS__>;\

#define INSTANTIATE_COMPARABLE_TYPE(DEF, T, ...); \
    DEF template class VIS T<__VA_ARGS__>;

#define INSTANTIATE_MISC_TYPES(DEF) \
    DEF template class VIS MoveOnly<NonTrivial>; \
    DEF template class VIS MoveOnly<Trivial>; \
    DEF template class VIS Sink<bool>;


#define INSTANTIATE(EXTERN_KEYWORD) \
    INSTANTIATE_ITERATORS(EXTERN_KEYWORD, int); \
    INSTANTIATE_ITERATORS(EXTERN_KEYWORD, float); \
    INSTANTIATE_ITERATORS(EXTERN_KEYWORD, double); \
    INSTANTIATE_ITERATORS(EXTERN_KEYWORD, long); \
    INSTANTIATE_ITERATORS(EXTERN_KEYWORD, long long); \
    INSTANTIATE_ITERATORS(EXTERN_KEYWORD, std::string); \
    INSTANTIATE_ITERATORS(EXTERN_KEYWORD, std::vector<int>); \
    INSTANTIATE_MISC_TYPES(EXTERN_KEYWORD);

#endif

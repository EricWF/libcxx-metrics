#ifndef TEST_TYPES_IMPL_H
#define TEST_TYPES_IMPL_H
#include "test_types.h"
#include <vector>
#include <string>

namespace test_types {

#define DEFINE_EXTERN
#define EXTERN extern

#define VIS __attribute__((visibility("default")))

    

template<typename T, class Base>
ForwardIterator<T, Base>::ForwardIterator(): pos_(nullptr) {}

template<typename T, class Base>
ForwardIterator<T, Base>::ForwardIterator(T* pos): pos_(pos) {}

template<typename T, class Base>
ForwardIterator<T, Base>::ForwardIterator(const ForwardIterator& iter): pos_(iter.pos_) {}

template<typename T, class Base>
ForwardIterator<T, Base>::~ForwardIterator() = default;

template<typename T, class Base>
ForwardIterator<T, Base>& ForwardIterator<T, Base>::operator=(const ForwardIterator& iter) {
    pos_ = iter.pos_;
    return *this;
}

template<typename T, class Base>
bool ForwardIterator<T, Base> ::operator==(const ForwardIterator& RHS) const {
    return this->pos_ == RHS.pos_;
}


template<typename T, class Base>
bool ForwardIterator<T, Base> ::operator!=(const ForwardIterator& RHS) const {
    return this->pos_ != RHS.pos_;
}

template<typename T, class Base>
T& ForwardIterator<T, Base>::operator*() {
    return *pos_;
}

template<typename T, class Base>
T* ForwardIterator<T, Base>::operator->() {
    return pos_;
}

template<typename T, class Base>
ForwardIterator<T, Base>& ForwardIterator<T, Base>::operator++() {
    ++pos_;
    return *this;
}

template<typename T, class Base>
ForwardIterator<T, Base> ForwardIterator<T, Base>::operator++(int) {
    ForwardIterator temp = *this;
    this->pos_++;
    return temp;
}






template<typename T, class Base>
InputIterator<T, Base>::InputIterator(): pos_(nullptr) {}

template<typename T, class Base>
InputIterator<T, Base>::InputIterator(T* pos): pos_(pos) {}

template<typename T, class Base>
InputIterator<T, Base>::InputIterator(const InputIterator& iter): pos_(iter.pos_) {}

template<typename T, class Base>
InputIterator<T, Base>::~InputIterator() = default;

template<typename T, class Base>
InputIterator<T, Base>& InputIterator<T, Base>::operator=(const InputIterator& iter) {
    pos_ = iter.pos_;
    return *this;
}

template<typename T, class Base>
bool InputIterator<T, Base> ::operator==(const InputIterator& RHS) const {
    return this->pos_ == RHS.pos_;
}


template<typename T, class Base>
bool InputIterator<T, Base> ::operator!=(const InputIterator& RHS) const {
    return this->pos_ != RHS.pos_;
}

template<typename T, class Base>
T& InputIterator<T, Base>::operator*() {
    return *pos_;
}

template<typename T, class Base>
T* InputIterator<T, Base>::operator->() {
    return pos_;
}

template<typename T, class Base>
InputIterator<T, Base>& InputIterator<T, Base>::operator++() {
    ++pos_;
    return *this;
}

template<typename T, class Base>
InputIterator<T, Base> InputIterator<T, Base>::operator++(int) {
    InputIterator temp = *this;
    this->pos_++;
    return temp;
}


// Constructor
template<typename T, class Base>
BidirectionalIterator<T, Base>::BidirectionalIterator() : pos_(nullptr) {}

// Constructor with position
template<typename T, class Base>
BidirectionalIterator<T, Base>::BidirectionalIterator(T* pos) : pos_(pos) {}

// Copy Constructor
template<typename T, class Base>
BidirectionalIterator<T, Base>::BidirectionalIterator(const BidirectionalIterator& iter) : pos_(iter.pos_) {}

// Destructor
template<typename T, class Base>
BidirectionalIterator<T, Base>::~BidirectionalIterator() = default;

// Assignment operator
template<typename T, class Base>
BidirectionalIterator<T, Base>& BidirectionalIterator<T, Base>::operator=(const BidirectionalIterator& iter) {
    pos_ = iter.pos_;
    return *this;
}

// Equality comparison operator
template<typename T, class Base>
bool BidirectionalIterator<T, Base>::operator==(const BidirectionalIterator& RHS ) const {
    return this->pos_ == RHS.pos_;
}

// Inequality comparison operator
template<typename T, class Base>
bool BidirectionalIterator<T, Base>::operator!=(const BidirectionalIterator& RHS ) const {
    return this->pos_ != RHS.pos_;
}

// Dereference operator
template<typename T, class Base>
T& BidirectionalIterator<T, Base>::operator*() const {
    return *pos_;
}

// Arrow operator
template<typename T, class Base>
T* BidirectionalIterator<T, Base>::operator->() const {
    return pos_;
}

// Pre-increment operator
template<typename T, class Base>
BidirectionalIterator<T, Base>& BidirectionalIterator<T, Base>::operator++() {
    ++pos_;
    return *this;
}

// Post-increment operator
template<typename T, class Base>
BidirectionalIterator<T, Base> BidirectionalIterator<T, Base>::operator++(int) {
    BidirectionalIterator temp = *this;
    this->pos_++;
    return temp;
}

// Pre-decrement operator
template<typename T, class Base>
BidirectionalIterator<T, Base>& BidirectionalIterator<T, Base>::operator--() {
    --pos_;
    return *this;
}

// Post-decrement operator
template<typename T, class Base>
BidirectionalIterator<T, Base> BidirectionalIterator<T, Base>::operator--(int) {
    BidirectionalIterator temp = *this;
    this->pos_--;
    return temp;
}


template<typename T, class Base>
RandomAccessIterator<T, Base>::RandomAccessIterator(T* pos) : pos_(pos) {}

template<typename T, class Base>
RandomAccessIterator<T, Base>::RandomAccessIterator() : pos_(nullptr) {}

template<typename T, class Base>
RandomAccessIterator<T, Base>::RandomAccessIterator(const RandomAccessIterator& iter) : pos_(iter.pos_) {}

template<typename T, class Base>
RandomAccessIterator<T, Base>::~RandomAccessIterator() {}

template<typename T, class Base>
RandomAccessIterator<T, Base>& RandomAccessIterator<T, Base>::operator=(const RandomAccessIterator& iter) {
    pos_ = iter.pos_;
    return *this;
}


template<typename T, class Base>
T& RandomAccessIterator<T, Base>::operator*() const {
    return *pos_;
}

template<typename T, class Base>
T* RandomAccessIterator<T, Base>::operator->() const {
    return pos_;
}

template<typename T, class Base>
RandomAccessIterator<T, Base>& RandomAccessIterator<T, Base>::operator++() {
    ++pos_;
    return *this;
}

template<typename T, class Base>
RandomAccessIterator<T, Base> RandomAccessIterator<T, Base>::operator++(int) {
    RandomAccessIterator<T, Base> tmp(*this);
    ++pos_;
    return tmp;
}


template<typename T, class Base>
bool RandomAccessIterator<T, Base>::operator==(const RandomAccessIterator& rhs) const {
    return this->pos_ == rhs.pos_;
}

template<typename T, class Base>
bool RandomAccessIterator<T, Base>::operator!=(const RandomAccessIterator& rhs) const {
    return this->pos_ != rhs.pos_;
}

template<typename T, class Base>
bool RandomAccessIterator<T, Base>::operator<(const RandomAccessIterator& rhs) const {
    return this->pos_ < rhs.pos_;
}

template<typename T, class Base>
bool RandomAccessIterator<T, Base>::operator<=(const RandomAccessIterator& rhs) const {
    return this->pos_ <= rhs.pos_;
}

template<typename T, class Base>
bool RandomAccessIterator<T, Base>::operator>(const RandomAccessIterator& rhs) const {
    return this->pos_ > rhs.pos_;
}

template<typename T, class Base>
bool RandomAccessIterator<T, Base>::operator>=(const RandomAccessIterator& rhs) const {
    return this->pos_ >= rhs.pos_;
}

template <class Ret>
template <class ...Args>
Ret Sink<Ret>::operator()(Args&&... args) const {
    return Ret();
}

template <class T, class ...Args>
T  Transformer::operator()(T&& v, Args&&... args) const {
    return std::forward<T>(v);
}

} // namespace test_types


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
    INSTANTIATE_MISC_TYPES(EXTERN_KEYWORD)

namespace test_types {
INSTANTIATE(extern);
}

#endif // TEST_TYPES_IMPL_H

#ifndef LIBCXX_METRICS_INPUTS_INCLUDE_TEST_TYPES_H
#define LIBCXX_METRICS_INPUTS_INCLUDE_TEST_TYPES_H
#include <iterator>

#define DEF_EQ(T) \
  friend bool operator==(T const&, T const&) noexcept; \
  friend bool operator!=(T const&, T const&) noexcept; \
  friend bool operator<(T const&, T const&) noexcept



namespace test_types {

constexpr struct InitTagT {} InitTag{};

struct NonTrivial {
  NonTrivial();
  explicit NonTrivial(int);
  NonTrivial(InitTagT);
  NonTrivial(NonTrivial const&);
  NonTrivial(NonTrivial &&) noexcept;
  NonTrivial& operator=(NonTrivial const&);
  NonTrivial& operator=(NonTrivial&&) noexcept;
  ~NonTrivial();

DEF_EQ(NonTrivial);

  int buff[10];
};


struct Trivial {
  Trivial() = default;
  Trivial(InitTagT);
  explicit Trivial(int) noexcept;
  Trivial(Trivial const&) = default;
  Trivial(Trivial&&) = default;
  Trivial& operator=(Trivial const&) = default;
  Trivial& operator=(Trivial &&) = default;
  ~Trivial() = default;

DEF_EQ(Trivial);
  int buff[10];
};

template <class Base = Trivial>
struct MoveOnly : Base {
  MoveOnly(MoveOnly const&) = delete;
  MoveOnly(MoveOnly&&) = default;
  MoveOnly() = default;
  MoveOnly& operator=(MoveOnly const&) = delete;
  MoveOnly& operator=(MoveOnly&&) = default;
  DEF_EQ(MoveOnly);
};


template<typename T, class Base = Trivial>
class ForwardIterator {
public:
    using iterator_category = std::forward_iterator_tag;
    using value_type = T;
    using difference_type = std::ptrdiff_t;
    using pointer = value_type*;
    using reference = value_type&;

    // Constructor
    ForwardIterator();

    // Copy Constructor
    ForwardIterator(const ForwardIterator& iter);

    // Destructor
    ~ForwardIterator();

    // Assignment operator
    ForwardIterator& operator=(const ForwardIterator& iter);

    // Equality comparison operator
    bool operator==(const ForwardIterator& iter) const;

    // Inequality comparison operator
    bool operator!=(const ForwardIterator& iter) const;

    // Dereference operator
    T& operator*();

    // Arrow operator
    T* operator->();

    // Pre-increment operator
    ForwardIterator& operator++();

    // Post-increment operator
    ForwardIterator operator++(int);
private:
  Trivial obj_;
};


template<typename T, class Base = Trivial>
class InputIterator {
public:
    using iterator_category = std::input_iterator_tag;
    using value_type = T;
    using difference_type = std::ptrdiff_t;
    using pointer = value_type*;
    using reference = value_type&;

    // Constructor
    InputIterator();

    // Copy Constructor
    InputIterator(const InputIterator& iter);

    // Destructor
    ~InputIterator();

    // Assignment operator
    InputIterator& operator=(const InputIterator& iter);

    // Equality comparison operator
    bool operator==(const InputIterator& iter) const;

    // Inequality comparison operator
    bool operator!=(const InputIterator& iter) const;

    // Dereference operator
    T& operator*();

    // Arrow operator
    T* operator->();

    // Pre-increment operator
    InputIterator& operator++();

    // Post-increment operator
    InputIterator operator++(int);
private:
  Base obj_;
};


template<typename T, class Base = Trivial>
class BidirectionalIterator {
public:
    using iterator_category = std::bidirectional_iterator_tag;
    using value_type = T;
    using difference_type = std::ptrdiff_t;
    using pointer = value_type*;
    using reference = value_type&;

    // Constructor
    BidirectionalIterator();

    // Copy Constructor
    BidirectionalIterator(const BidirectionalIterator& iter);

    // Destructor
    ~BidirectionalIterator();

    // Assignment operator
    BidirectionalIterator& operator=(const BidirectionalIterator& iter);

    // Equality comparison operator
    bool operator==(const BidirectionalIterator& iter) const;

    // Inequality comparison operator
    bool operator!=(const BidirectionalIterator& iter) const;

    // Dereference operator
    T& operator*() const;

    // Arrow operator
    T* operator->() const;

    // Pre-increment operator
    BidirectionalIterator& operator++();

    // Post-increment operator
    BidirectionalIterator operator++(int);

    // Pre-decrement operator
    BidirectionalIterator& operator--();

    // Post-decrement operator
    BidirectionalIterator operator--(int);

private:
    Base trivial;
};

template<typename T, class Base = Trivial>
class RandomAccessIterator {
public:
    using iterator_category = std::random_access_iterator_tag;
    using value_type = T;
    using difference_type = std::ptrdiff_t;
    using pointer = value_type*;
    using reference = value_type&;

    // Constructor
    RandomAccessIterator();

    // Copy Constructor
    RandomAccessIterator(const RandomAccessIterator& iter);

    // Destructor
    ~RandomAccessIterator();

    // Assignment operator
    RandomAccessIterator& operator=(const RandomAccessIterator& iter);

    // Equality comparison operator
    bool operator==(const RandomAccessIterator& iter) const;

    // Inequality comparison operator
    bool operator!=(const RandomAccessIterator& iter) const;

    // Dereference operator
    T& operator*() const;

    // Arrow operator
    T* operator->() const;

    // Pre-increment operator
    RandomAccessIterator& operator++();

    // Post-increment operator
    RandomAccessIterator operator++(int);

    // Pre-decrement operator
    RandomAccessIterator& operator--();

    // Post-decrement operator
    RandomAccessIterator operator--(int);

    // Addition operator
    RandomAccessIterator& operator+=(const int& add);

    // Subtraction operator
    RandomAccessIterator& operator-=(const int& sub);

    // Less than comparison operator
    bool operator<(const RandomAccessIterator& iter) const;

    // Greater than comparison operator
    bool operator>(const RandomAccessIterator& iter) const;

    // Less than or equal to comparison operator
    bool operator<=(const RandomAccessIterator& iter) const;

    // Greater than or equal to comparison operator
    bool operator>=(const RandomAccessIterator& iter) const;

    // Subscript operator
    T& operator[](const int& index) const;

    friend RandomAccessIterator operator+(RandomAccessIterator, std::ptrdiff_t);
    friend RandomAccessIterator operator-(RandomAccessIterator, std::ptrdiff_t);
    RandomAccessIterator& operator+=(std::ptrdiff_t);
    RandomAccessIterator& operator-=(std::ptrdiff_t);

    friend std::ptrdiff_t operator-(RandomAccessIterator,RandomAccessIterator);


private:
    Base obj_;  // pointer to the current element
};


template<typename T, class Base = Trivial>
class OutputIterator {
public:
    using iterator_category = std::output_iterator_tag;
    using value_type = T;
    using difference_type = std::ptrdiff_t;
    using pointer = value_type*;
    using reference = value_type&;

    // Constructor
    OutputIterator();

    // Copy Constructor
    OutputIterator(const OutputIterator& iter);

    // Destructor
    ~OutputIterator();

    // Assignment operator
    OutputIterator& operator=(const OutputIterator& iter);

    // Equality comparison operator
    bool operator==(const OutputIterator& iter) const;

    // Inequality comparison operator
    bool operator!=(const OutputIterator& iter) const;

    // Dereference operator
    T& operator*() const;

    // Arrow operator
    T* operator->() const;

    // Pre-increment operator
    OutputIterator& operator++();

    // Post-increment operator
    OutputIterator operator++(int);

    // Pre-decrement operator
    OutputIterator& operator--();

    // Post-decrement operator
    OutputIterator operator--(int);

    // Addition operator
    OutputIterator& operator+=(const int& add);

    // Subtraction operator
    OutputIterator& operator-=(const int& sub);

    // Less than comparison operator
    bool operator<(const OutputIterator& iter) const;

    // Greater than comparison operator
    bool operator>(const OutputIterator& iter) const;

    // Less than or equal to comparison operator
    bool operator<=(const OutputIterator& iter) const;

    // Greater than or equal to comparison operator
    bool operator>=(const OutputIterator& iter) const;

private:
    Base obj_;  // pointer to the current element
};


template <class Ret>
struct Sink {
  using result_type = Ret;
  template <class ...Args>
  Ret operator()(Args&&...) const;
};

using Predicate = Sink<bool>;
using BinaryPredicate = Sink<bool>;
using Compare = Sink<bool>;

struct Transformer {
  template <class T, class ...Args>
  T operator()(T&& v, Args&&...) const;
};
using Function = Transformer;
using UnaryOp = Transformer;
using UnaryOperator = Transformer;
using UnaryOperation = Transformer;
using BinaryOperation = Transformer;
using Size = std::size_t;
using Distance = std::ptrdiff_t;

using RandomNumberGenerator = Sink<unsigned long>;

struct UniformRandomBitGenerator {

  template <class G>
  unsigned int operator()(G&&) const;

  static unsigned int max();
  static unsigned int min();
};
struct UniformRandomNumberGenerator{
  using result_type = unsigned int;
  unsigned int operator()() const;

  static constexpr unsigned int max() { return 0; }
  static constexpr unsigned int min() { return 10000;}
};
}

#endif // LIBCXX_METRICS_INPUTS_INCLUDE_TEST_TYPES_H

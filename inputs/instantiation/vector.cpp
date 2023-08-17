#include "test_types.h"
#include <vector>
#include <cassert>
#include <array>
using namespace test_types;


void sink(const void*);

template <class T>
__attribute__((always_inline))
inline void use(T&& v) {
  sink(&v);
}

template <class T>
struct TestSuite {
  std::vector<T> vec;
  std::vector<T> vec1;
  std::vector<T> const& const_vec;
  T value;
  const T const_value;

  using VecT = std::vector<T>;
  using Ref = typename std::vector<T>::reference;
  using CRef = typename std::vector<T>::const_reference;
  using Iter = typename std::vector<T>::iterator;
  using CIter = typename std::vector<T>::const_iterator;
  
  void  allocator_constructor()
  {
      std::allocator<T> alloc;
      std::vector<T, std::allocator<T>> v(alloc);
      use(v);
  }
  
  void test_at() {
      use(vec.at(0));
  }

  Ref back() {
    return vec.back();
  }

  std::size_t capacity() {
    return vec.capacity();
  }


  void clear() {
    vec.clear();
  }


  Ref const_at() {
    return vec.at(0);
  }

  CRef const_back() {
      return const_vec.back();
      // ... assertions to verify the 'back' reference ...
  }

  const T* const_data() {
    return vec.data();
  }

  CRef const_index_operator(int n) {
    return const_vec[n];
  }

  VecT copy_allocator_constructor() {
    
    std::allocator<T> alloc;
    std::vector<T> copy(const_vec, alloc);
    return copy;
  }

  void copy_assignment() {
    vec = const_vec;
  }



  VecT copy_constructor() {
    VecT new_v(const_vec);
    return new_v;
  }




  T* data_test() {
    return vec.data();
  }



  VecT default_constructor() {
      VecT vec;
      return vec;
  }


  void test_emplace() {
    std::vector<T> v{{}};
    auto it = vec.begin();
    vec.emplace(it, 42);
  }


  void test_emplace_back() {
    vec.emplace_back(101);
  }


  bool test_vector_empty() {
      return  vec.empty();
  }


  Iter erase_pos() {
    auto iter = vec.begin() + 2;
    return vec.erase(iter);
  }



  Iter erase_range() {
    return vec.erase(vec.begin() + 2, vec.begin() + 5);
  }


  Ref test_front() {
    return vec.front();
  }


  CRef front_const() {
    return const_vec.front();
  }



  std::allocator<T> get_allocator() {
      return vec.get_allocator();
  }


  VecT ilist_alloc_constructor() {
    std::allocator<Trivial> alloc;
    std::vector<T> vec({value, value}, alloc);
    return vec;
  }


  Ref index_operator(std::size_t n) {
    return vec[n];
  }


  Iter insert_input_range(InputIterator<T> begin, InputIterator<T> end, unsigned N) {

    return vec.insert(vec.begin()+N, begin, end);

  }


  Iter insert_pos_ilist(unsigned N) {

    return vec.insert(vec.begin() + N, {value, value, value});
  }


  Iter insert_pos_size_value(CIter pos, unsigned N) {
    return vec.insert(pos, N, value);
  }



  Iter insert_pos_value(Iter pos) {

      return vec.insert(pos, value);
  }



  std::size_t test_max_size() {
    return vec.max_size();
  }



  VecT move_alloc_constructor(VecT& orig) {
    std::allocator<NonTrivial> alloc;
    std::vector<T> copy(std::move(orig), alloc);
    return copy;
  }

  void move_assignment(VecT&& other) {
    vec = std::move(other);
  }


  VecT move_constructor(VecT& obj) {
    VecT  v(std::move(obj));
    return v;

  }

  VecT n_default_items_constructor(std::size_t itemCount) {
      VecT v(itemCount);
      return vec;
  }

std::vector<T>  n_items_constructor(std::size_t N) {
  return std::vector<T>(N, value, std::allocator<T>());
  
}

  bool op_greater(std::vector<T> const& LHS, std::vector<T> const& RHS) {
    return LHS > RHS;
  }
  bool op_greater_eq(std::vector<T> const& LHS, std::vector<T> const& RHS) {
    return LHS >= RHS;
  }
  bool op_less(std::vector<T> const& LHS, std::vector<T> const& RHS) {
    return LHS < RHS;
  }
  bool op_less_equal(std::vector<T> const& LHS, std::vector<T> const& RHS) {
    return LHS <= RHS;
  }
  bool op_equal(std::vector<T> const& LHS, std::vector<T> const& RHS) {
    return LHS == RHS;
  }

  bool op_not_equal(std::vector<T> const& LHS, std::vector<T> const& RHS) {
    return LHS != RHS;
  }


  void operator_assign_ilist() {
      vec = {InitTag, InitTag, InitTag};
  }


  void pop_back() {
    vec.pop_back();
  }


  void test_push_back() {
    vec.push_back(value);
  }


  void push_back_rvalue(T value) {
    vec.push_back(std::move(value));
  }


  void reserve() {
      vec.reserve(10);
  }


  void resize() {

    vec.resize(7, value);

  }


  void shrink_to_fit() {
      vec.shrink_to_fit();
  }


  std::size_t test_size() {
    return vec.size();
  }


  void swap() {
    vec.swap(vec1);
  }
}; // end class

template class TestSuite<Trivial>;

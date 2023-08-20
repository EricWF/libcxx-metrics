
#include <algorithm>
#include <iterator>
#include <tuple>
#include <vector>
#include <array>


#include "test_types.h"

using std::iterator_traits;
using std::pair;

template <class T>
struct Tester {
    using InputIterator = test_types::InputIterator<T>;
    using Predicate = test_types::Predicate;
    using Function = test_types::Function;
    using Size = test_types::Size;
    using ForwardIterator1 = test_types::ForwardIterator<T>;
    using ForwardIterator2 = test_types::ForwardIterator<T>;
    using BinaryPredicate = test_types::BinaryPredicate;
    using ForwardIterator = test_types::ForwardIterator<T>;
    using InputIterator1 = test_types::InputIterator<T>;
    using InputIterator2 = test_types::InputIterator<T>;
    using OutputIterator = test_types::OutputIterator<T>;
    using BidirectionalIterator1 = test_types::BidirectionalIterator<T>;
    using BidirectionalIterator2 = test_types::BidirectionalIterator<T>;
    using UnaryOperation = test_types::UnaryOperation;
    using BinaryOperation = test_types::BinaryOperation;
    using Generator = test_types::Sink<T>;
    using BidirectionalIterator = test_types::BidirectionalIterator<T>;
    using RandomAccessIterator = test_types::RandomAccessIterator<T>;
    using RandomNumberGenerator = test_types::RandomNumberGenerator;
    using PopulationIterator = test_types::ForwardIterator<T>;
    using SampleIterator = test_types::ForwardIterator<T>;
    using Distance = test_types::Distance;
    using UniformRandomBitGenerator = test_types::UniformRandomBitGenerator;
    using UniformRandomNumberGenerator = test_types::UniformRandomNumberGenerator;
    using OutputIterator1 = test_types::OutputIterator<T>;
    using OutputIterator2 = test_types::OutputIterator<T>;
    using Compare = test_types::Compare;

    
    
    
    bool test_all_of(InputIterator first, InputIterator last, Predicate pred) {
      return std::all_of(first, last, pred);
    }
    
    
    bool test_any_of(InputIterator first, InputIterator last, Predicate pred) {
      return std::any_of(first, last, pred);
    }
    
    
    bool test_none_of(InputIterator first, InputIterator last, Predicate pred) {
      return std::none_of(first, last, pred);
    }
    
    
    Function test_for_each(InputIterator first, InputIterator last, Function f) {
      return std::for_each(first, last, f);
    }
    
    /*
        InputIterator test_for_each_n(InputIterator first, Size n, Function f) {
      return std::for_each_n(first, n, f);
    }
    */
    
    InputIterator test_find_if(InputIterator first, InputIterator last, Predicate pred) {
      return std::find_if(first, last, pred);
    }
    
    
    InputIterator test_find_if_not(InputIterator first, InputIterator last, Predicate pred) {
      return std::find_if_not(first, last, pred);
    }
    
    
    ForwardIterator1 test_find_end(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2, ForwardIterator2 last2) {
      return std::find_end(first1, last1, first2, last2);
    }
    
    
    ForwardIterator1 test_find_end(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2, ForwardIterator2 last2, BinaryPredicate pred) {
      return std::find_end(first1, last1, first2, last2, pred);
    }
    
    
    ForwardIterator1 test_find_first_of(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2, ForwardIterator2 last2) {
     return std::find_first_of(first1, last1, first2, last2);
    }
    
    
    ForwardIterator1 test_find_first_of(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2, ForwardIterator2 last2, BinaryPredicate pred) {
      return std::find_first_of(first1, last1, first2, last2, pred);
    }
    
    
    ForwardIterator test_adjacent_find(ForwardIterator first, ForwardIterator last) {
      return std::adjacent_find(first, last);
    }
    
    
    ForwardIterator test_adjacent_find(ForwardIterator first, ForwardIterator last, BinaryPredicate pred) {
      return std::adjacent_find(first, last, pred);
    }
    
    
    typename iterator_traits<InputIterator>::difference_type test_count(InputIterator first, InputIterator last, const T& value) {
      return std::count(first, last, value);
    }
    
    
    typename iterator_traits<InputIterator>::difference_type test_count_if(InputIterator first, InputIterator last, Predicate pred) {
      return std::count_if(first, last, pred);
    }
    
    
    pair<InputIterator1, InputIterator2> test_mismatch(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2) {
      return std::mismatch(first1, last1, first2);
    }
    
    
    std::pair<InputIterator1, InputIterator2> test_mismatch(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, BinaryPredicate pred) {
      return std::mismatch(first1, last1, first2, last2, pred);
    }
    
    
    bool test_equal(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2) {
      return std::equal(first1, last1, first2);
    }
    
    
    bool test_equal(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2) {
      return std::equal(first1, last1, first2, last2);
    }
    
    
    bool test_equal(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, BinaryPredicate pred) {
      return std::equal(first1, last1, first2, pred);
    }
    
    
    bool test_equal(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, BinaryPredicate pred) {
      return std::equal(first1, last1, first2, last2, pred);
    }
    
    
    bool test_is_permutation(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2) {
      return std::is_permutation(first1, last1, first2);
    }
    
    
    bool test_is_permutation(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2, ForwardIterator2 last2) {
      return std::is_permutation(first1, last1, first2, last2);
    }
    
    
    bool test_is_permutation(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2, BinaryPredicate pred) {
      return std::is_permutation(first1, last1, first2, pred);
    }
    
    
    bool test_is_permutation(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2, ForwardIterator2 last2, BinaryPredicate pred) {
      return std::is_permutation(first1, last1, first2, last2, pred);
    }
    
    
    ForwardIterator1 test_search(ForwardIterator1 first1, ForwardIterator1 last1,
    ForwardIterator2 first2, ForwardIterator2 last2) {
      return std::search(first1, last1, first2, last2);
    }
    
    
    ForwardIterator1 test_search(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2, ForwardIterator2 last2, BinaryPredicate pred) {
      return std::search(first1, last1, first2, last2, pred);
    }
    
    
    
    ForwardIterator test_search(BinaryPredicate pred, ForwardIterator first, ForwardIterator last, Size count, const T& value) {
      return std::search_n(first, last, count, value, pred);
    }
    
    
    OutputIterator test_copy(InputIterator first, InputIterator last, OutputIterator result) {
      return std::copy(first, last, result);
    }
    
    
    OutputIterator test_copy_if(InputIterator first, InputIterator last, OutputIterator result, Predicate pred) {
      return std::copy_if(first, last, result, pred);
    }
    
    
    OutputIterator test_copy_n(InputIterator first, Size n, OutputIterator result) {
      return std::copy_n(first, n, result);
    }
    
    
    BidirectionalIterator2 test_copy_backward(BidirectionalIterator1 first, BidirectionalIterator1 last, BidirectionalIterator2 result) {
      return std::copy_backward(first, last, result);
    }
    
    
    ForwardIterator2 test_swap_ranges(ForwardIterator1 first1, ForwardIterator1 last1, ForwardIterator2 first2) {
      return std::swap_ranges(first1, last1, first2);
    }
    
    
    void test_iter_swap(ForwardIterator1 a, ForwardIterator2 b) {
      std::iter_swap(a, b);
    }
    
    
    OutputIterator test_transform(InputIterator first, InputIterator last, OutputIterator result, UnaryOperation op) {
      return std::transform(first, last, result, op);
    }
    
    
    OutputIterator test_transform(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, OutputIterator result, BinaryOperation binary_op) {
     return std::transform(first1, last1, first2, result, binary_op); 
    }
    
    
    void test_replace(ForwardIterator first, ForwardIterator last, const T& old_value, const T& new_value) {
      std::replace(first, last, old_value, new_value);
    }
    
    
    void test_replace_if(ForwardIterator first, ForwardIterator last, Predicate pred, const T& new_value) {
      std::replace_if(first, last, pred, new_value);
    }
    
    
    OutputIterator test_replace_copy(InputIterator first, InputIterator last, OutputIterator result, const T& old_value, const T& new_value) {
      return std::replace_copy(first, last, result, old_value, new_value);
    }
    
    
    OutputIterator test_replace_copy_if(InputIterator first, InputIterator last, OutputIterator result, Predicate pred, const T& new_value) {
      return std::replace_copy_if(first, last, result, pred, new_value);
    }
    
    
    void test_fill(ForwardIterator first, ForwardIterator last, const T& value) {
      std::fill(first, last, value); 
    }
    
    
    OutputIterator test_fill_n(OutputIterator first, Size n, const T& value) {
      return std::fill_n(first, n, value);
    }
    
    
    void test_generate(ForwardIterator first, ForwardIterator last, Generator gen) {
      std::generate(first, last, gen);
    }
    
    
    OutputIterator test_generate_n(OutputIterator first, Size n, Generator gen) {
     return std::generate_n(first, n, gen);
    }
    
    
    ForwardIterator test_remove(ForwardIterator first, ForwardIterator last, const T& value) {
      return std::remove(first, last, value);
    }
    
    
    ForwardIterator test_remove_if(ForwardIterator first, ForwardIterator last, Predicate pred) {
      return std::remove_if(first, last, pred);
    }
    
    
    OutputIterator test_remove_copy(InputIterator first, InputIterator last, OutputIterator result, const T& value) {
      return std::remove_copy(first, last, result, value);
    }
    
    
    OutputIterator test_remove_copy_if(InputIterator first, InputIterator last, OutputIterator result, Predicate pred) {
      return std::remove_copy_if(first, last, result, pred);
    }
    
    
    OutputIterator test_unique_copy(InputIterator first, InputIterator last, OutputIterator result) {
      return std::unique_copy(first, last, result);
    }
    
    
    void test_reverse(BidirectionalIterator first, BidirectionalIterator last) {
      std::reverse(first, last);
    }
    
    
    OutputIterator test_reverse_copy(BidirectionalIterator first, BidirectionalIterator last, OutputIterator result) {
      return std::reverse_copy(first, last, result);
    }
    
    
    ForwardIterator test_rotate(ForwardIterator first, ForwardIterator middle, ForwardIterator last) {
      return std::rotate(first, middle, last);
    }
/*
    SampleIterator test_sample(PopulationIterator first, PopulationIterator last, SampleIterator out, Distance n, UniformRandomBitGenerator&& g) {
      return std::sample(first, last, out, n, std::forward<UniformRandomBitGenerator>(g));
    }
  */

        void test_shuffle(RandomAccessIterator first, RandomAccessIterator last, UniformRandomNumberGenerator&& g) {
      std::shuffle(first, last, std::forward<UniformRandomNumberGenerator>(g));
    }
    
    
    bool test_is_partitioned(InputIterator first, InputIterator last, Predicate pred) {
      return std::is_partitioned(first, last, pred);
    }
    
    
    ForwardIterator test_partition(ForwardIterator first, ForwardIterator last, Predicate pred) {
      return std::partition(first, last, pred);
    }
    
    
    std::pair<OutputIterator1, OutputIterator2> test_partition_copy(InputIterator first, InputIterator last, OutputIterator1 out_true, OutputIterator2 out_false, Predicate pred) {
      return std::partition_copy(first, last, out_true, out_false, pred);
    }
    
    
    ForwardIterator test_partition_point(ForwardIterator first, ForwardIterator last, Predicate pred) {
      return std::partition_point(first, last, pred);
    }

        bool test_is_sorted(ForwardIterator first, ForwardIterator last) {
      return std::is_sorted(first, last);
    }
    
    
    
        bool is_sorted_test(ForwardIterator first, ForwardIterator last, Compare comp) {
      return std::is_sorted(first, last, comp);
    }
    

    ForwardIterator test_is_sorted_until(ForwardIterator first, ForwardIterator last) {
      return std::is_sorted_until(first, last);
    }
    
    
    
    ForwardIterator test_is_sorted_until(ForwardIterator first, ForwardIterator last, Compare comp) {
      return std::is_sorted_until(first, last, comp);
    }
    
    
    void test_sort(RandomAccessIterator first, RandomAccessIterator last) {
      std::sort(first, last);
    }
    
    
    void test_sort(RandomAccessIterator first, RandomAccessIterator last, Compare comp) {
      std::sort(first, last, comp);
    }
    
    
    void test_stable_sort(RandomAccessIterator first, RandomAccessIterator last) {
      std::stable_sort(first, last);
    }
    
    
    void test_stable_sort(RandomAccessIterator first, RandomAccessIterator last, Compare comp) {
      std::stable_sort(first, last, comp);
    }
    
    
    void test_partial_sort(RandomAccessIterator first, RandomAccessIterator middle, RandomAccessIterator last) {
      std::partial_sort(first, middle, last);
    }
    
    
    void test_partial_sort(RandomAccessIterator first, RandomAccessIterator middle, RandomAccessIterator last, Compare comp) {
      std::partial_sort(first, middle, last, comp);
    }
    
    
    RandomAccessIterator test_partial_sort_copy(InputIterator first, InputIterator last, RandomAccessIterator result_first, RandomAccessIterator result_last) {
      return std::partial_sort_copy(first, last, result_first, result_last);
    }
    
    
    RandomAccessIterator test_partial_sort_copy(InputIterator first, InputIterator last,
    RandomAccessIterator result_first, RandomAccessIterator result_last, Compare comp) {
      return std::partial_sort_copy(first, last, result_first, result_last, comp);
    }
    
    
    void test_nth_element(RandomAccessIterator first, RandomAccessIterator nth, RandomAccessIterator last) {
      std::nth_element(first, nth, last);
    }
    
    
    void test_nth_element(RandomAccessIterator first, RandomAccessIterator nth, RandomAccessIterator last, Compare comp) {
      std::nth_element(first, nth, last, comp);
    }
    
    
    
    ForwardIterator test_lower_bound(ForwardIterator first, ForwardIterator last, const T& value) {
      return std::lower_bound(first, last, value);
    }
    
    
    ForwardIterator test_lower_bound(ForwardIterator first, ForwardIterator last, const T& value, Compare comp) {
      return std::lower_bound(first, last, value, comp);
    }
    
    
    ForwardIterator test_upper_bound(ForwardIterator first, ForwardIterator last, const T& value) {
      return std::upper_bound(first, last, value);
    }
    
    
    ForwardIterator test_upper_bound(ForwardIterator first, ForwardIterator last, const T& value, Compare comp) {
      return std::upper_bound(first, last, value, comp);
    }
    
    
    pair<ForwardIterator, ForwardIterator> test_equal_range(ForwardIterator first, ForwardIterator last, const T& value, Compare comp) {
      return std::equal_range(first, last, value, comp);
    }
    
    
    bool test_binary_search(ForwardIterator first, ForwardIterator last, const T& value) {
      return std::binary_search(first, last, value);
    }
    
    
    bool test_binary_search(ForwardIterator first, ForwardIterator last, const T& value, Compare comp) {
      return std::binary_search(first, last, value, comp);
    }
    
    
    
    OutputIterator test_merge(InputIterator1 first1, InputIterator1 last1,
    InputIterator2 first2, InputIterator2 last2, OutputIterator result) {
      return std::merge(first1, last1, first2, last2, result);
    }
    
    
    OutputIterator test_merge(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, OutputIterator result, Compare comp) {
      return std::merge(first1, last1, first2, last2, result, comp);
    }
    
    
    void test_inplace_merge(BidirectionalIterator first, BidirectionalIterator middle, BidirectionalIterator last) {
      std::inplace_merge(first, middle, last);
    }
    
    
    void test_inplace_merge(BidirectionalIterator first, BidirectionalIterator middle, BidirectionalIterator last, Compare comp) {
      std::inplace_merge(first, middle, last, comp);
    }
    
    
    bool test_includes(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, Compare comp) {
      return std::includes(first1, last1, first2, last2, comp);
    }
    
    
    OutputIterator test_set_union(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, OutputIterator result) {
      return std::set_union(first1, last1, first2, last2, result);
    }
    
    
    OutputIterator test_set_union(InputIterator1 first1, InputIterator1 last1,
    InputIterator2 first2, InputIterator2 last2, OutputIterator result, Compare comp) {
      return std::set_union(first1, last1, first2, last2, result, comp);
    }
    
    
    OutputIterator test_set_intersection(InputIterator1 first1, InputIterator1 last1,
    InputIterator2 first2, InputIterator2 last2, OutputIterator result) {
      return std::set_intersection(first1, last1, first2, last2, result);
    }
    
    
    OutputIterator test_set_intersection(InputIterator1 first1, InputIterator1 last1,
    InputIterator2 first2, InputIterator2 last2, OutputIterator result, Compare comp) {
      return std::set_intersection(first1, last1, first2, last2, result, comp);
    }
    
    
    OutputIterator test_set_difference(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, OutputIterator result) {
      return std::set_difference(first1, last1, first2, last2, result);
    }
    
    
    OutputIterator test_set_difference(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, OutputIterator result, Compare comp) {
      return std::set_difference(first1, last1, first2, last2, result, comp);
    }
    
    
    OutputIterator test_set_symmetric_difference(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, OutputIterator result) {
      return std::set_symmetric_difference(first1, last1, first2, last2, result);
    }
    
    
    OutputIterator test_set_symmetric_difference(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2, OutputIterator result, Compare comp) {
      return std::set_symmetric_difference(first1, last1, first2, last2, result, comp);
    }
    
    
    void test_push_heap(RandomAccessIterator first, RandomAccessIterator last) {
      std::push_heap(first, last);
    }
    
    
    void test_push_heap(RandomAccessIterator first, RandomAccessIterator last, Compare comp) {
      std::push_heap(first, last, comp);
    }
    
    
    void test_pop_heap(RandomAccessIterator first, RandomAccessIterator last) {
      std::pop_heap(first, last);
    }
    
    
    void test_pop_heap(RandomAccessIterator first, RandomAccessIterator last, Compare comp) {
      std::pop_heap(first, last, comp);
    }
    
    
    
    void test_make_heap(RandomAccessIterator first, RandomAccessIterator last) {
      std::make_heap(first, last);
    }
    
    
    void test_make_heap(RandomAccessIterator first, RandomAccessIterator last, Compare comp) {
      std::make_heap(first, last, comp);
    }
    
    
    void test_sort_heap(RandomAccessIterator first, RandomAccessIterator last) {
      std::sort_heap(first, last);
    }
    
    
    void test_sort_heap(RandomAccessIterator first, RandomAccessIterator last, Compare comp) {
      std::sort_heap(first, last, comp);
    }
    
    
    bool test_is_heap(RandomAccessIterator first, RandomAccessIterator last) {
      return std::is_heap(first, last);
    }
    
    
    bool test_is_heap(RandomAccessIterator first, RandomAccessIterator last, Compare comp) {
      return std::is_heap(first, last, comp);
    }
    
    
    RandomAccessIterator test_is_heap_until(RandomAccessIterator first, RandomAccessIterator last) {
      return std::is_heap_until(first, last);
    }
    
    
    ForwardIterator test_min_element(ForwardIterator first, ForwardIterator last) {
      return std::min_element(first, last);
    }
    
    
    ForwardIterator test_min_element(ForwardIterator first, ForwardIterator last, Compare comp) {
      return std::min_element(first, last, comp);
    }
    
    
    T test_min(const T& a, const T& b) {
      return std::min(a, b);
    }
    
    
    T test_min(const T& a, const T& b, Compare comp) {
      return std::min(a, b, comp);
    }
    
    
    T test_min(std::initializer_list<T> t) {
      return std::min(t);
    }
    
    
    T test_min(std::initializer_list<T> t, Compare comp) {
      return std::min(t, comp);
    }
    

    /*
    const T& test_clamp(const T& v, const T& lo, const T& hi ) {
      return std::clamp(v, lo, hi);
    }
    
    
    const T& test_clamp(const T& v, const T& lo, const T& hi, Compare comp) {
      return std::clamp(v, lo, hi, comp);
    }
    
*/

    ForwardIterator test_max_element(ForwardIterator first, ForwardIterator last) {
      return std::max_element(first, last);
    }
    
    
    ForwardIterator test_max_element(ForwardIterator first, ForwardIterator last, Compare comp) {
      return std::max_element(first, last, comp);
    }
    
    
    T test_max(const T& a, const T& b) {
      return std::max(a, b);
    }
    
    
    T test_max(const T& a, const T& b, Compare comp) {
      return std::max(a, b, comp); 
    }
    
    
    T test_max(std::initializer_list<T> t) {
      return std::max(t);
    }
    
    
    pair<ForwardIterator, ForwardIterator> test_minmax_element(ForwardIterator first, ForwardIterator last) {
      return std::minmax_element(first, last);
    }
    
    
    std::pair<ForwardIterator, ForwardIterator> test_minmax_element(ForwardIterator first, ForwardIterator last, Compare comp) {
      return std::minmax_element(first, last, comp);
    }
    
    
    pair<const T&, const T&> test_minmax(const T& a, const T& b) {
      return std::minmax(a, b);
    }
    
    
    pair<const T&, const T&> test_minmax(const T& a, const T& b, Compare comp) {
      return std::minmax(a, b, comp);
    }
    
    
    
    std::pair<T, T> test_minmax(std::initializer_list<T> t) {
      return std::minmax(t);
    }
    
    
    std::pair<T, T> test_minmax(std::initializer_list<T> t, Compare comp) {
      return std::minmax(t, comp);
    }
    
    
    bool test_lexicographical_compare(InputIterator1 first1, InputIterator1 last1, InputIterator2 first2, InputIterator2 last2) {
      return std::lexicographical_compare(first1, last1, first2, last2);
    }
    
    
    bool test_next_permutation(BidirectionalIterator first, BidirectionalIterator last) {
      return std::next_permutation(first, last);
    }
    
    
    bool test_next_permutation(BidirectionalIterator first, BidirectionalIterator last, Compare comp) {
      return std::next_permutation(first, last, comp);
    }
    
    
    bool test_prev_permutation(BidirectionalIterator first, BidirectionalIterator last) {
      return std::prev_permutation(first, last);
    }
    
    
    bool test_prev_permutation(BidirectionalIterator first, BidirectionalIterator last, Compare comp) {
      return std::prev_permutation(first, last, comp);
    }
    
    
    T test_max(std::initializer_list<T> t, Compare comp) {
      return std::max(t, comp);
    }
};

template struct Tester<int>;

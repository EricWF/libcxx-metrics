
#include <algorithm>
#include <iterator>
#include <tuple>
#include <vector>
#include <array>
#include <utility>
#include <unordered_map>

#include "test_types.h"

template <class ...Args>
struct Pack;

template <class ...Args> struct Pack;
template <class Key, class T, class Hash = std::hash<Key>, class Pred = std::equal_to<Key>, 
    class Allocator =  std::allocator<std::pair<const Key, T> >, class Arg1 = Pack<int> >
struct Tester;



template <class Key, class T, class Hash, class Pred, class Allocator, class ...Args> 
struct Tester<Key, T, Hash, Pred, Allocator, Pack<Args...> > {
    using MapT = std::unordered_map<Key, T, Hash, Pred, Allocator>;
    using key_type             = Key;
    using mapped_type          = T;
    using value_type           = std::pair<const Key, T>;
    using hasher               = Hash;
    using key_equal            = Pred;
    using allocator_type       = Allocator;
    using pointer              = typename std::allocator_traits<Allocator>::pointer;
    using const_pointer        = typename std::allocator_traits<Allocator>::const_pointer;
    using reference            = value_type&;
    using const_reference      = const value_type&;
    using size_type            = typename MapT::size_type;
    using difference_type      = typename MapT::difference_type;

    using iterator             = typename MapT::iterator;
    using const_iterator       = typename MapT::const_iterator;
    using local_iterator       = typename MapT::local_iterator;
    using const_local_iterator = typename MapT::const_local_iterator;
    using InputIterator = test_types::InputIterator<std::pair<Key, T>>;
  


    
    
    /* unordered_map()  */
    MapT test_default_constructor() {
      MapT map;
      return map;
    }
    
    /* unordered_map(size_type n, const hasher& hf = hasher(), const key_equal& eql = key_equal(), const allocator_type& a = allocator_type())  */

    
    MapT test_unordered_map_constructor(size_type n, const hasher& hf = hasher(), const key_equal& eql = key_equal(), const allocator_type& a = allocator_type()) {
      MapT map(n, hf, eql, a);
      return map;
    }
    
    /* unordered_map(const unordered_map&)  */
    MapT test_unordered_map_copy_constructor(const MapT& other) {
     MapT map(other);
     return map;
    }
    
    /* unordered_map(unordered_map&&)  */
    MapT test_move_constructor(MapT&& src) {
      MapT map(std::move(src));
      return map;
    }
    
    /* unordered_map(initializer_list<value_type> il, size_type n = see below, const hasher& hf = hasher(), const key_equal& eql = key_equal(), const allocator_type& a = allocator_type())  */

    
    MapT test_unordered_map_constructor_initialize_list(std::initializer_list<value_type> il, size_type n, const hasher& hf, const key_equal& eql, const allocator_type& a) {
      MapT map(il, n, hf, eql, a);
      return map;
    }
    
    /* ~unordered_map()  */
    void test_unordered_map_destructor(MapT& map) {
      map.~MapT();
    }
    
    /* unordered_map& operator=(const unordered_map&)  */

    
    MapT& test_operator_assign_copy(MapT& map1, const MapT& map2) {
      map1 = map2;
      return map1;
    }
    
    /* unordered_map& operator=(unordered_map&&) noexcept(allocator_traits<Allocator>::is_always_equal::value && is_nothrow_move_assignable_v<Hash> && is_nothrow_move_assignable_v<Pred>)  */


    
    static void test_operator_assignment_move() {
      std::unordered_map<Key, T, Hash, Pred, Allocator> map1, map2;
    
      map1 = std::move(map2);
    }
    
    
    /* unordered_map& operator=(initializer_list<value_type>)  */


    
    using MapType = std::unordered_map<Key, T, Hash, Pred, Allocator>;
    
    MapType& test_map_assign_initializer_list(MapType& map, std::initializer_list<value_type> ilist) {
      return map = ilist;
    }
    
    /* allocator_type get_allocator() const noexcept  */
    allocator_type test_get_allocator(const MapT& map) {
      return map.get_allocator();
    }
    
    /* const_iterator begin() const noexcept  */
    typename MapT::const_iterator test_begin(const MapT& m) {
        return m.begin();
    }
    
    /* iterator end() noexcept  */
    iterator test_end(MapT& map) {
      return map.end();
    }
    
    /* const_iterator end() const noexcept  */
    /* const_iterator end() const noexcept  */
    const_iterator test_end_const_noexcept(const MapT& map) {
      return map.end();
    }
    
    /* const_iterator cbegin() const noexcept  */
    const_iterator test_cbegin(const MapT& map) {
      return map.cbegin();
    }
    
    /* const_iterator cend() const noexcept  */
    const_iterator test_cend(const MapT& map) {
      return map.cend();
    }
    
    /* bool empty() const noexcept  */
    bool test_empty(const MapT& map) {
      return map.empty();
    }
    
    /* size_type size() const noexcept  */
    size_type test_size(const MapT& map) {
      return map.size();
    }
    
    /* size_type max_size() const noexcept  */
    
    size_type test_max_size(const MapT& map) {
      return map.max_size();
    }
    
    /* iterator insert(const_iterator hint, const value_type& obj)  */

    
    iterator test_insert_with_hint_and_value(MapT& map, const_iterator hint, const value_type& obj) {
      return map.insert(hint, obj);
    }
    
    /* void insert(InputIterator first, InputIterator last)  */

    
    template <typename InputIterator>
    void test_insert_range(std::unordered_map<Key, T, Hash, Pred, Allocator>& m, InputIterator first, InputIterator last) {
      m.insert(first, last);
    }
    
    /* void insert(initializer_list<value_type>)  */
    void test_insert_initializer_list(MapT& map, std::initializer_list<typename MapT::value_type> List) {
      map.insert(List);
    }



    
    /* iterator erase(iterator position)  */
    auto test_erase_iterator(MapT& map, iterator position) {
            return map.erase(position);
    }
    
    /* iterator erase(const_iterator first, const_iterator last)  */
    iterator test_erase_range(MapT& map, const_iterator first, const_iterator last) {
      return map.erase(first, last);
    }
    
    /* void swap(unordered_map&) noexcept(allocator_traits<Allocator>::is_always_equal::value && is_nothrow_swappable_v<Hash> && is_nothrow_swappable_v<Pred>)  */
    void test_unordered_map_swap(Tester::MapT& map1, Tester::MapT& map2) {
      map1.swap(map2);
    }
    
    /* void clear() noexcept  */
    void test_clear(MapT& map) {
      map.clear();
    }
    /* hasher hash_function() const  */
    hasher test_hash_function(MapT& map) { return map.hash_function();}
    
    /* key_equal key_eq() const  */
    key_equal test_key_eq(MapT& map) { return map.key_eq(); }
    
    /* iterator find(const key_type& k)  */
    iterator test_find_with_key(MapT& map, const key_type& k) { return map.find(k); }
    
    /* const_iterator find(const key_type& k) const  */
    const_iterator test_find(const MapT& map, const key_type& k) {
      return map.find(k);
    }
    
    /* size_type count(const key_type& k) const  */
    size_type test_count_with_key(MapT& map, const key_type& k) {
      return map.count(k);
    }
    
    /* pair<iterator, iterator> equal_range(const key_type& k)  */


    
    
    std::pair<Tester::iterator, Tester::iterator> test_equal_range(Tester::MapT& map, const Tester::key_type& k) {
      return map.equal_range(k);
    }
    
    /* mapped_type& operator[](const key_type& k)  */

    
    mapped_type& test_bracket_operator(MapT& map, const key_type& k) {
      return map[k];
    }
    
    /* mapped_type& operator[](key_type&& k)  */
    mapped_type& test_operator_subscript_rvalue_key(MapT& map, key_type&& k) {
      return map[k];
    }
    
    /* mapped_type& at(const key_type& k)  */
    mapped_type& test_at_with_key(MapT& map, const key_type& k) {
      return map.at(k);
    }
    
    /* const mapped_type& at(const key_type& k) const  */

    
    const T& test_at(const std::unordered_map<Key, T, Hash, Pred, Allocator>& map, const Key& k) {
      return map.at(k);
    }
    
    /* size_type bucket_count() const noexcept  */
    size_type test_bucket_count_const_noexcept(MapT& map) { return map.bucket_count(); }
    
    /* size_type bucket_size(size_type n) const  */
    size_type test_bucket_size(const MapT& map, size_type n) {
      return map.bucket_size(n);
    }
    
    /* size_type bucket(const key_type& k) const  */
    /* size_type bucket(const key_type& k) const  */
    size_type test_bucket(const MapT& map, const key_type& k) {
      return map.bucket(k);
    }
    
    /* local_iterator begin(size_type n)  */
    local_iterator test_begin(MapT& m, size_type n) {
      return m.begin(n);
    }
    
    /* const_local_iterator begin(size_type n) const  */
    const_local_iterator test_begin_n(const MapT& map, size_type n) {
      return map.begin(n);
    }
    
    /* local_iterator end(size_type n)  */
    local_iterator test_end(MapT& map, size_type n) { return map.end(n); }
    
    /* const_local_iterator end(size_type n) const  */
    const_local_iterator test_end(const MapT& map, size_type n) {
      return map.end(n);
    }
    
    /* const_local_iterator cbegin(size_type n) const  */
    const_local_iterator test_cbegin(const MapT& map, size_type n) {
      return map.cbegin(n);
    }
    
    /* float load_factor() const noexcept  */
    float test_load_factor(const MapT& map) {
      return map.load_factor();
    }
    
    /* float max_load_factor() const noexcept  */
    float test_max_load_factor(const MapT& map) {
      return map.max_load_factor();
    }
    
    /* void max_load_factor(float z)  */
    void test_max_load_factor(MapT& map, float z) {
      map.max_load_factor(z);
    }
    
    /* void rehash(size_type n)  */
    void test_rehash(MapT& map, typename MapT::size_type n) {
      map.rehash(n);
    }
    
    /* void reserve(size_type n)  */
    void test_reserve(MapT& map, size_type n) {
      map.reserve(n);
    }
    
    /* unordered_map(InputIterator f, InputIterator l, size_type n = see below, const hasher& hf = hasher(), const key_equal& eql = key_equal(), const allocator_type& a = allocator_type())  */
    MapT test_unordered_map_constructor_with_iterators(InputIterator f, InputIterator l, size_type n, const hasher& hf = hasher(), const key_equal& eql = key_equal(), const allocator_type& a = allocator_type()) {
        MapT map(f, l, n, hf, eql, a);
        return map;
    }
    
    /* unordered_map(const unordered_map&, const type_identity_t<Allocator>&)  */
    MapT test_unordered_map_constructor(MapT& other, Allocator alloc) {
        MapT map(other, alloc);
        return map;
    }
    
    /* unordered_map(unordered_map&&, const type_identity_t<Allocator>&)  */
    MapT test_unordered_map_move_constructor(MapT&& m, const allocator_type& a) {
        MapT map(std::move(m), a);
        return map;
    }
    
    /* iterator insert(const_iterator hint, value_type&& obj)  */
    iterator test_insert_hint_value(MapT& map, const_iterator hint, value_type&& obj) {
        return map.insert(hint, std::move(obj));
    }


    /* iterator emplace_hint(const_iterator position, Args&&... args)  */

    
    std::unordered_map<int, int>::iterator test_unordered_map_emplace_hint(std::unordered_map<int, int>& map, std::unordered_map<int, int>::const_iterator position, int key, int value) {
    	return map.emplace_hint(position, std::make_pair(key, value));
    }
};

template struct Tester<int, int>;


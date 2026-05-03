export interface Course {
  id: string;
  code: string;
  name: string;
  instructor: string;
  color: string;
  progress: number;
  enrolled: number;
  image: string;
  description: string;
  schedule: string;
  status: 'in-progress' | 'featured' | 'not-started' | 'completed';
}

export interface Assignment {
  id: string;
  courseId: string;
  courseName: string;
  courseColor: string;
  title: string;
  dueDate: string;
  status: 'pending' | 'submitted' | 'graded' | 'overdue';
  points: number;
  earnedPoints?: number;
  difficulty?: 'Easy' | 'Medium' | 'Hard';
  type?: 'code' | 'essay' | 'quiz';
}

export interface CodingProblem {
  id: string;
  assignmentId: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  description: string;
  problemConstraint?: string;
  examples: {
    input: string;
    output: string;
    explanation?: string;
  }[];
  constraints: string[];
  functionSkeleton: {
    python: string;
    javascript: string;
    java: string;
    cpp: string;
  };
  testCases: {
    input: string;
    expectedOutput: string;
    hidden: boolean;
  }[];
  hints?: string[];
  topics: string[];
}

export interface Grade {
  courseId: string;
  courseName: string;
  courseColor: string;
  grade: number;
  assignments: {
    name: string;
    points: number;
    maxPoints: number;
    date: string;
  }[];
}

export interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time: string;
  type: 'assignment' | 'exam' | 'lecture' | 'event';
  courseColor: string;
}

export interface Message {
  id: string;
  sender: string;
  subject: string;
  preview: string;
  date: string;
  read: boolean;
  avatar: string;
}

export const courses: Course[] = [
  {
    id: '1',
    code: 'CS101',
    name: 'Nhập môn lập trình',
    instructor: 'TS. Nguyễn Văn A',
    color: 'bg-[#030391]',
    progress: 68,
    enrolled: 145,
    image: 'ai-digital-economy',
    description: 'Khóa học giới thiệu các khái niệm cơ bản về lập trình, bao gồm biến, vòng lặp, điều kiện, hàm và cấu trúc dữ liệu cơ bản. Sử dụng ngôn ngữ Python.',
    schedule: 'Thứ 2, Thứ 4 14:00 - 16:00',
    status: 'in-progress',
  },
  {
    id: '2',
    code: 'CS102',
    name: 'Cấu trúc Dữ liệu và Giải thuật',
    instructor: 'TS. Trần Thị B',
    color: 'bg-[#1488D8]',
    progress: 45,
    enrolled: 132,
    image: 'fintech-blockchain',
    description: 'Học về các cấu trúc dữ liệu như Array, Linked List, Stack, Queue, Tree, Graph và các thuật toán sắp xếp, tìm kiếm, đệ quy.',
    schedule: 'Thứ 3, Thứ 5 10:00 - 12:00',
    status: 'in-progress',
  },
  {
    id: '3',
    code: 'CS103',
    name: 'Kỹ thuật lập trình',
    instructor: 'TS. Lê Văn C',
    color: 'bg-[#42A5F5]',
    progress: 82,
    enrolled: 98,
    image: 'design-thinking',
    description: 'Nâng cao kỹ năng lập trình với OOP, Design Patterns, Clean Code, Testing và các best practices trong phát triển phần mềm.',
    schedule: 'Thứ 2, Thứ 6 09:00 - 11:00',
    status: 'featured',
  },
  {
    id: '4',
    code: 'CS104',
    name: 'Nhập môn điện toán',
    instructor: 'PGS. Phạm Văn D',
    color: 'bg-[#6C63FF]',
    progress: 0,
    enrolled: 87,
    image: 'algorithmic-trading',
    description: 'Giới thiệu về kiến trúc máy tính, hệ điều hành, mạng máy tính và các khái niệm nền tảng trong khoa học máy tính.',
    schedule: 'Thứ 4, Thứ 6 13:00 - 15:00',
    status: 'not-started',
  },
  {
    id: '5',
    code: 'CS201',
    name: 'Lập trình Web',
    instructor: 'ThS. Hoàng Thị E',
    color: 'bg-[#00B4D8]',
    progress: 55,
    enrolled: 156,
    image: 'marketing-analytics',
    description: 'Học HTML, CSS, JavaScript, React, Node.js và xây dựng ứng dụng web fullstack hiện đại với database.',
    schedule: 'Thứ 3, Thứ 5 14:00 - 16:00',
    status: 'in-progress',
  },
  {
    id: '6',
    code: 'CS202',
    name: 'Lập trình Mobile',
    instructor: 'TS. Võ Văn F',
    color: 'bg-[#2A9D8F]',
    progress: 70,
    enrolled: 110,
    image: 'sustainable-business',
    description: 'Phát triển ứng dụng di động đa nền tảng với React Native, Flutter, UI/UX design và tích hợp API.',
    schedule: 'Thứ 2, Thứ 4 16:00 - 18:00',
    status: 'in-progress',
  },
  {
    id: '7',
    code: 'CS301',
    name: 'Trí tuệ nhân tạo',
    instructor: 'PGS. Đỗ Văn G',
    color: 'bg-[#8B5CF6]',
    progress: 38,
    enrolled: 178,
    image: 'algorithmic-trading',
    description: 'Khám phá Machine Learning, Deep Learning, Neural Networks, Computer Vision và Natural Language Processing.',
    schedule: 'Thứ 3, Thứ 6 08:00 - 10:00',
    status: 'in-progress',
  },
  {
    id: '8',
    code: 'CS302',
    name: 'An toàn thông tin',
    instructor: 'TS. Bùi Thị H',
    color: 'bg-[#F59E0B]',
    progress: 52,
    enrolled: 142,
    image: 'marketing-analytics',
    description: 'Tìm hiểu về bảo mật mạng, mã hóa, phát hiện xâm nhập, ethical hacking và các kỹ thuật bảo vệ hệ thống.',
    schedule: 'Thứ 4, Thứ 5 15:00 - 17:00',
    status: 'in-progress',
  },
];

export const assignments: Assignment[] = [
  {
    id: '1',
    courseId: '1',
    courseName: 'Nhập môn lập trình',
    courseColor: 'bg-[#030391]',
    title: 'Two Sum - Tìm hai số có tổng bằng target',
    dueDate: '2026-02-17T23:59:00',
    status: 'pending',
    points: 100,
    difficulty: 'Easy',
    type: 'code',
  },
  {
    id: '2',
    courseId: '2',
    courseName: 'Cấu trúc Dữ liệu và Giải thuật',
    courseColor: 'bg-[#1488D8]',
    title: 'Binary Search Tree - Triển khai cây tìm kiếm nhị phân',
    dueDate: '2026-02-16T23:59:00',
    status: 'pending',
    points: 150,
    difficulty: 'Hard',
    type: 'code',
  },
  {
    id: '3',
    courseId: '3',
    courseName: 'Kỹ thuật lập trình',
    courseColor: 'bg-[#42A5F5]',
    title: 'Design Patterns - Báo cáo về Singleton và Factory',
    dueDate: '2026-02-20T23:59:00',
    status: 'pending',
    points: 120,
    difficulty: 'Medium',
    type: 'essay',
  },
  {
    id: '4',
    courseId: '1',
    courseName: 'Nhập môn lập trình',
    courseColor: 'bg-[#030391]',
    title: 'Palindrome Number - Kiểm tra số palindrome',
    dueDate: '2026-02-10T23:59:00',
    status: 'submitted',
    points: 80,
    difficulty: 'Easy',
    type: 'code',
  },
  {
    id: '5',
    courseId: '5',
    courseName: 'Lập trình Web',
    courseColor: 'bg-[#00B4D8]',
    title: 'Todo App - Xây dựng ứng dụng quản lý công việc',
    dueDate: '2026-02-15T23:59:00',
    status: 'pending',
    points: 90,
    difficulty: 'Medium',
    type: 'code',
  },
  {
    id: '6',
    courseId: '3',
    courseName: 'Kỹ thuật lập trình',
    courseColor: 'bg-[#42A5F5]',
    title: 'Unit Testing - Viết test cases cho Shopping Cart',
    dueDate: '2026-02-08T23:59:00',
    status: 'graded',
    points: 100,
    earnedPoints: 92,
    difficulty: 'Medium',
    type: 'code',
  },
  {
    id: '7',
    courseId: '6',
    courseName: 'Lập trình Mobile',
    courseColor: 'bg-[#2A9D8F]',
    title: 'Weather App - Tích hợp API thời tiết',
    dueDate: '2026-02-22T23:59:00',
    status: 'pending',
    points: 110,
    difficulty: 'Hard',
    type: 'code',
  },
  {
    id: '8',
    courseId: '2',
    courseName: 'Cấu trúc Dữ liệu và Giải thuật',
    courseColor: 'bg-[#1488D8]',
    title: 'Merge Sort - Sắp xếp mảng bằng thuật toán merge sort',
    dueDate: '2026-02-05T23:59:00',
    status: 'graded',
    points: 100,
    earnedPoints: 88,
    difficulty: 'Medium',
    type: 'code',
  },
  {
    id: '9',
    courseId: '7',
    courseName: 'Trí tuệ nhân tạo',
    courseColor: 'bg-[#8B5CF6]',
    title: 'Linear Regression - Dự đoán giá nhà',
    dueDate: '2026-02-18T23:59:00',
    status: 'pending',
    points: 100,
    difficulty: 'Medium',
    type: 'code',
  },
  {
    id: '10',
    courseId: '8',
    courseName: 'An toàn thông tin',
    courseColor: 'bg-[#F59E0B]',
    title: 'Caesar Cipher - Mã hóa và giải mã văn bản',
    dueDate: '2026-02-21T23:59:00',
    status: 'pending',
    points: 120,
    difficulty: 'Easy',
    type: 'code',
  },
];

export const codingProblems: CodingProblem[] = [
  {
    id: '1',
    assignmentId: '1',
    title: 'Two Sum',
    difficulty: 'Easy',
    description: `Cho một mảng số nguyên nums và một số nguyên target, trả về chỉ số của hai số mà tổng của chúng bằng target.

Bạn có thể giả định rằng mỗi input sẽ có chính xác một solution, và bạn không thể sử dụng cùng một phần tử hai lần.

Bạn có thể trả về answer theo bất kỳ thứ tự nào.`,
    examples: [
      { 
        input: 'nums = [2,7,11,15], target = 9', 
        output: '[0,1]',
        explanation: 'Vì nums[0] + nums[1] == 9, chúng ta trả về [0, 1].'
      },
      { 
        input: 'nums = [3,2,4], target = 6', 
        output: '[1,2]' 
      },
      { 
        input: 'nums = [3,3], target = 6', 
        output: '[0,1]' 
      },
    ],
    problemConstraint: `2 <= nums.length <= 10^4
-10^9 <= nums[i] <= 10^9
-10^9 <= target <= 10^9
Chỉ có duy nhất một solution hợp lệ`,
    constraints: [
      '2 <= nums.length <= 10^4',
      '-10^9 <= nums[i] <= 10^9',
      '-10^9 <= target <= 10^9',
      'Chỉ có duy nhất một solution hợp lệ'
    ],
    functionSkeleton: {
      python: `def twoSum(nums, target):
    """
    :type nums: List[int]
    :type target: int
    :rtype: List[int]
    """
    # Viết code của bạn ở đây
    pass

# Test
print(twoSum([2,7,11,15], 9))  # Expected: [0,1]`,
      javascript: `function twoSum(nums, target) {
    /**
     * @param {number[]} nums
     * @param {number} target
     * @return {number[]}
     */
    // Viết code của bạn ở đây
}

// Test
console.log(twoSum([2,7,11,15], 9));  // Expected: [0,1]`,
      java: `class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Viết code của bạn ở đây
        return new int[]{};
    }
    
    public static void main(String[] args) {
        Solution solution = new Solution();
        int[] result = solution.twoSum(new int[]{2,7,11,15}, 9);
        System.out.println(Arrays.toString(result)); // Expected: [0, 1]
    }
}`,
      cpp: `#include <vector>
#include <iostream>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Viết code của bạn ở đây
        return {};
    }
};

int main() {
    Solution solution;
    vector<int> nums = {2, 7, 11, 15};
    vector<int> result = solution.twoSum(nums, 9);
    // Expected: [0, 1]
    return 0;
}`,
    },
    testCases: [
      { input: '[2,7,11,15], 9', expectedOutput: '[0,1]', hidden: false },
      { input: '[3,2,4], 6', expectedOutput: '[1,2]', hidden: false },
      { input: '[3,3], 6', expectedOutput: '[0,1]', hidden: true },
      { input: '[-1,-2,-3,-4,-5], -8', expectedOutput: '[2,4]', hidden: true },
    ],
    hints: [
      'Hãy sử dụng hash map để lưu trữ các số đã gặp',
      'Với mỗi số, kiểm tra xem target - nums[i] có trong hash map không',
      'Độ phức tạp thời gian có thể đạt O(n)'
    ],
    topics: ['Array', 'Hash Table'],
  },
  {
    id: '2',
    assignmentId: '4',
    title: 'Palindrome Number',
    difficulty: 'Easy',
    description: `Cho một số nguyên x, trả về true nếu x là số palindrome (số đối xứng), ngược lại trả về false.

Số palindrome là số mà khi đọc từ trái sang phải và từ phải sang trái đều giống nhau.`,
    examples: [
      { 
        input: 'x = 121', 
        output: 'true',
        explanation: '121 đọc từ trái sang phải là 121. Từ phải sang trái cũng là 121.'
      },
      { 
        input: 'x = -121', 
        output: 'false',
        explanation: 'Từ trái sang phải, đọc là -121. Từ phải sang trái, đọc là 121-. Do đó, không phải là palindrome.'
      },
      { 
        input: 'x = 10', 
        output: 'false',
        explanation: 'Đọc từ phải sang trái là 01. Do đó, không phải là palindrome.'
      },
    ],
    problemConstraint: `-2^31 <= x <= 2^31 - 1`,
    constraints: [
      '-2^31 <= x <= 2^31 - 1'
    ],
    functionSkeleton: {
      python: `def isPalindrome(x):
    """
    :type x: int
    :rtype: bool
    """
    # Viết code của bạn ở đây
    pass

# Test
print(isPalindrome(121))  # Expected: True
print(isPalindrome(-121))  # Expected: False`,
      javascript: `function isPalindrome(x) {
    /**
     * @param {number} x
     * @return {boolean}
     */
    // Viết code của bạn ở đây
}

// Test
console.log(isPalindrome(121));  // Expected: true
console.log(isPalindrome(-121));  // Expected: false`,
      java: `class Solution {
    public boolean isPalindrome(int x) {
        // Viết code của bạn ở đây
        return false;
    }
    
    public static void main(String[] args) {
        Solution solution = new Solution();
        System.out.println(solution.isPalindrome(121));  // Expected: true
        System.out.println(solution.isPalindrome(-121));  // Expected: false
    }
}`,
      cpp: `#include <iostream>
using namespace std;

class Solution {
public:
    bool isPalindrome(int x) {
        // Viết code của bạn ở đây
        return false;
    }
};

int main() {
    Solution solution;
    cout << solution.isPalindrome(121) << endl;  // Expected: 1 (true)
    cout << solution.isPalindrome(-121) << endl;  // Expected: 0 (false)
    return 0;
}`,
    },
    testCases: [
      { input: '121', expectedOutput: 'true', hidden: false },
      { input: '-121', expectedOutput: 'false', hidden: false },
      { input: '10', expectedOutput: 'false', hidden: false },
      { input: '0', expectedOutput: 'true', hidden: true },
      { input: '12321', expectedOutput: 'true', hidden: true },
    ],
    hints: [
      'Số âm không thể là palindrome',
      'Bạn có thể đảo ngược một nửa số và so sánh với nửa còn lại',
      'Tránh overflow bằng cách chỉ đảo ngược một nửa số'
    ],
    topics: ['Math'],
  },
  {
    id: '3',
    assignmentId: '8',
    title: 'Merge Sort',
    difficulty: 'Medium',
    description: `Triển khai thuật toán Merge Sort để sắp xếp một mảng số nguyên theo thứ tự tăng dần.

Merge Sort là một thuật toán chia để trị (divide and conquer) chia mảng thành hai nửa, sắp xếp từng nửa và sau đó merge chúng lại.`,
    examples: [
      { 
        input: 'arr = [12, 11, 13, 5, 6, 7]', 
        output: '[5, 6, 7, 11, 12, 13]'
      },
      { 
        input: 'arr = [38, 27, 43, 3, 9, 82, 10]', 
        output: '[3, 9, 10, 27, 38, 43, 82]'
      },
    ],
    problemConstraint: `0 <= arr.length <= 5000
-10^6 <= arr[i] <= 10^6`,
    constraints: [
      '0 <= arr.length <= 5000',
      '-10^6 <= arr[i] <= 10^6'
    ],
    functionSkeleton: {
      python: `def mergeSort(arr):
    """
    :type arr: List[int]
    :rtype: List[int]
    """
    if len(arr) <= 1:
        return arr
    
    # Viết code của bạn ở đây
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]
    
    # Recursively sort both halves
    # ...
    
    # Merge the sorted halves
    # ...
    
    return arr

# Test
print(mergeSort([12, 11, 13, 5, 6, 7]))`,
      javascript: `function mergeSort(arr) {
    /**
     * @param {number[]} arr
     * @return {number[]}
     */
    if (arr.length <= 1) {
        return arr;
    }
    
    // Viết code của bạn ở đây
    const mid = Math.floor(arr.length / 2);
    const left = arr.slice(0, mid);
    const right = arr.slice(mid);
    
    // Recursively sort both halves
    // ...
    
    // Merge the sorted halves
    // ...
    
    return arr;
}

// Test
console.log(mergeSort([12, 11, 13, 5, 6, 7]));`,
      java: `import java.util.Arrays;

class Solution {
    public int[] mergeSort(int[] arr) {
        if (arr.length <= 1) {
            return arr;
        }
        
        // Viết code của bạn ở đây
        int mid = arr.length / 2;
        
        // Split array into two halves
        // Sort recursively
        // Merge the sorted halves
        
        return arr;
    }
    
    public static void main(String[] args) {
        Solution solution = new Solution();
        int[] arr = {12, 11, 13, 5, 6, 7};
        System.out.println(Arrays.toString(solution.mergeSort(arr)));
    }
}`,
      cpp: `#include <vector>
#include <iostream>
using namespace std;

class Solution {
public:
    vector<int> mergeSort(vector<int>& arr) {
        if (arr.size() <= 1) {
            return arr;
        }
        
        // Viết code của bạn ở đây
        int mid = arr.size() / 2;
        
        // Split array into two halves
        // Sort recursively
        // Merge the sorted halves
        
        return arr;
    }
};

int main() {
    Solution solution;
    vector<int> arr = {12, 11, 13, 5, 6, 7};
    vector<int> result = solution.mergeSort(arr);
    return 0;
}`,
    },
    testCases: [
      { input: '[12, 11, 13, 5, 6, 7]', expectedOutput: '[5, 6, 7, 11, 12, 13]', hidden: false },
      { input: '[38, 27, 43, 3, 9, 82, 10]', expectedOutput: '[3, 9, 10, 27, 38, 43, 82]', hidden: false },
      { input: '[1]', expectedOutput: '[1]', hidden: true },
      { input: '[]', expectedOutput: '[]', hidden: true },
      { input: '[5, 2, 3, 1]', expectedOutput: '[1, 2, 3, 5]', hidden: true },
    ],
    hints: [
      'Chia mảng thành hai nửa cho đến khi mỗi nửa chỉ có 1 phần tử',
      'Hàm merge cần so sánh các phần tử từ hai mảng đã sắp xếp và ghép chúng',
      'Độ phức tạp thời gian: O(n log n), không gian: O(n)'
    ],
    topics: ['Array', 'Divide and Conquer', 'Sorting', 'Merge Sort'],
  },
];

export const grades: Grade[] = [
  {
    courseId: '1',
    courseName: 'Nhập môn lập trình',
    courseColor: 'bg-[#030391]',
    grade: 88.5,
    assignments: [
      { name: 'Luận văn đạo đức AI', points: 90, maxPoints: 100, date: '2026-01-15' },
      { name: 'Triển khai mô hình ML', points: 85, maxPoints: 100, date: '2026-01-29' },
      { name: 'Thuyết trình nghiên cứu', points: 92, maxPoints: 100, date: '2026-02-05' },
    ],
  },
  {
    courseId: '2',
    courseName: 'Cấu trúc Dữ liệu và Giải thuật',
    courseColor: 'bg-[#1488D8]',
    grade: 91.2,
    assignments: [
      { name: 'Kiến trúc Blockchain', points: 95, maxPoints: 100, date: '2026-01-12' },
      { name: 'Phân tích giao thức DeFi', points: 88, maxPoints: 100, date: '2026-01-26' },
      { name: 'Báo cáo thị trường Crypto', points: 88, maxPoints: 100, date: '2026-02-05' },
    ],
  },
  {
    courseId: '3',
    courseName: 'Kỹ thuật lập trình',
    courseColor: 'bg-[#42A5F5]',
    grade: 93.7,
    assignments: [
      { name: 'Bài tập lập bản đồ cảm xúc', points: 95, maxPoints: 100, date: '2026-01-20' },
      { name: 'Phát triển nguyên mẫu', points: 92, maxPoints: 100, date: '2026-01-28' },
      { name: 'Báo cáo nghiên cứu người dùng', points: 92, maxPoints: 100, date: '2026-02-08' },
    ],
  },
  {
    courseId: '5',
    courseName: 'Lập trình Web',
    courseColor: 'bg-[#00B4D8]',
    grade: 87.3,
    assignments: [
      { name: 'Báo cáo tối ưu SEO', points: 85, maxPoints: 100, date: '2026-01-18' },
      { name: 'Phân tích mạng xã hội', points: 90, maxPoints: 100, date: '2026-02-01' },
      { name: 'Phân tích phễu chuyển đổi', points: 87, maxPoints: 100, date: '2026-02-10' },
    ],
  },
  {
    courseId: '6',
    courseName: 'Lập trình Mobile',
    courseColor: 'bg-[#2A9D8F]',
    grade: 90.5,
    assignments: [
      { name: 'Mô hình kinh tế tuần hoàn', points: 92, maxPoints: 100, date: '2026-01-22' },
      { name: 'Nghiên cứu đổi mới xanh', points: 89, maxPoints: 100, date: '2026-02-05' },
    ],
  },
  {
    courseId: '7',
    courseName: 'Trí tuệ nhân tạo',
    courseColor: 'bg-[#8B5CF6]',
    grade: 84.0,
    assignments: [
      { name: 'Bài kiểm tra ma trận', points: 82, maxPoints: 100, date: '2026-01-25' },
      { name: 'Xác suất thống kê', points: 86, maxPoints: 100, date: '2026-02-08' },
    ],
  },
  {
    courseId: '8',
    courseName: 'An toàn thông tin',
    courseColor: 'bg-[#F59E0B]',
    grade: 89.0,
    assignments: [
      { name: 'Nghiên cứu SAP Module', points: 91, maxPoints: 100, date: '2026-01-19' },
      { name: 'Quy trình kinh doanh', points: 87, maxPoints: 100, date: '2026-02-02' },
    ],
  },
];

export const calendarEvents: CalendarEvent[] = [
  {
    id: '1',
    title: 'AI Strategy Report Due',
    date: '2026-02-17',
    time: '11:59 PM',
    type: 'assignment',
    courseColor: 'bg-[#030391]',
  },
  {
    id: '2',
    title: 'FinTech Midterm Exam',
    date: '2026-02-16',
    time: '10:00 AM',
    type: 'exam',
    courseColor: 'bg-[#1488D8]',
  },
  {
    id: '3',
    title: 'Design Thinking Workshop',
    date: '2026-02-14',
    time: '09:00 AM',
    type: 'lecture',
    courseColor: 'bg-[#42A5F5]',
  },
  {
    id: '4',
    title: 'Innovation Presentation',
    date: '2026-02-20',
    time: '11:59 PM',
    type: 'assignment',
    courseColor: 'bg-[#42A5F5]',
  },
  {
    id: '5',
    title: 'Digital Marketing Lecture',
    date: '2026-02-15',
    time: '02:00 PM',
    type: 'lecture',
    courseColor: 'bg-[#00B4D8]',
  },
  {
    id: '6',
    title: 'ESG Framework Due',
    date: '2026-02-22',
    time: '11:59 PM',
    type: 'assignment',
    courseColor: 'bg-[#2A9D8F]',
  },
  {
    id: '7',
    title: 'UEH Tech Summit 2026',
    date: '2026-02-19',
    time: '10:00 AM',
    type: 'event',
    courseColor: 'bg-gray-500',
  },
];

export const messages: Message[] = [
  {
    id: '1',
    sender: 'Dr. Economic & Tech Expert',
    subject: 'AI Course: Office Hours This Week',
    preview: 'Just a reminder about my office hours on Thursday from 2-4 PM. We can discuss your AI strategy reports...',
    date: '2026-02-12T10:30:00',
    read: false,
    avatar: 'teacher-tech',
  },
  {
    id: '2',
    sender: 'Prof. Sarah Chen',
    subject: 'FinTech: Smart Contract Workshop',
    preview: 'We will have an additional workshop session on smart contract development next Tuesday...',
    date: '2026-02-12T08:15:00',
    read: false,
    avatar: 'teacher-fintech',
  },
  {
    id: '3',
    sender: 'UEH Academic Office',
    subject: 'Registration: Summer 2026',
    preview: 'Registration for Summer 2026 intensive programs opens on March 1st. Priority for current students...',
    date: '2026-02-11T14:20:00',
    read: true,
    avatar: 'admin',
  },
  {
    id: '4',
    sender: 'Dr. Michael Torres',
    subject: 'Design Thinking: Great Progress!',
    preview: 'Excellent work on your user research report. Your empathy mapping was particularly insightful...',
    date: '2026-02-10T16:45:00',
    read: true,
    avatar: 'teacher-design',
  },
  {
    id: '5',
    sender: 'UEH Innovation Lab',
    subject: 'Hackathon 2026: Registration Open',
    preview: 'The annual UEH Innovation Hackathon is back! Register your team by February 28th...',
    date: '2026-02-09T09:00:00',
    read: true,
    avatar: 'innovation',
  },
];

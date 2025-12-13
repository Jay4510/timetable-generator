// DMCE Information Technology Department - Complete Subject Data
// Based on actual curriculum and timetables

export interface Subject {
  id: string;
  name: string;
  code: string;
  year: string;
  semester: string;
  type: 'Theory' | 'Lab' | 'Tutorial' | 'Project';
  hoursPerWeek: number;
  faculty?: string[];
}

export const dmceITSubjects: Subject[] = [
  // Second Year (SE) - Semester III
  {
    id: 'se3_math3',
    name: 'Engineering Mathematics-III',
    code: 'MATH301',
    year: 'SE',
    semester: 'III',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. P. R. Desai']
  },
  {
    id: 'se3_oop',
    name: 'Object Oriented Programming with C++',
    code: 'IT301',
    year: 'SE',
    semester: 'III',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. S. K. Sharma']
  },
  {
    id: 'se3_oop_lab',
    name: 'OOP Lab',
    code: 'IT301L',
    year: 'SE',
    semester: 'III',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. S. K. Sharma']
  },
  {
    id: 'se3_ds',
    name: 'Data Structures',
    code: 'IT302',
    year: 'SE',
    semester: 'III',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. A. B. Patil']
  },
  {
    id: 'se3_ds_lab',
    name: 'Data Structures Lab',
    code: 'IT302L',
    year: 'SE',
    semester: 'III',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. A. B. Patil']
  },
  {
    id: 'se3_dbms',
    name: 'Database Management System',
    code: 'IT303',
    year: 'SE',
    semester: 'III',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. A. B. Patil']
  },
  {
    id: 'se3_dbms_lab',
    name: 'Database Management System Lab',
    code: 'IT303L',
    year: 'SE',
    semester: 'III',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. A. B. Patil']
  },
  {
    id: 'se3_cg',
    name: 'Computer Graphics',
    code: 'IT304',
    year: 'SE',
    semester: 'III',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Dr. R. M. Joshi']
  },
  {
    id: 'se3_cg_lab',
    name: 'Computer Graphics Lab',
    code: 'IT304L',
    year: 'SE',
    semester: 'III',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Dr. R. M. Joshi']
  },
  {
    id: 'se3_dld',
    name: 'Digital Logic Design and Analysis',
    code: 'IT305',
    year: 'SE',
    semester: 'III',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Dr. R. M. Joshi']
  },
  {
    id: 'se3_dld_lab',
    name: 'Digital Logic Design Lab',
    code: 'IT305L',
    year: 'SE',
    semester: 'III',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Dr. R. M. Joshi']
  },

  // Second Year (SE) - Semester IV
  {
    id: 'se4_cn',
    name: 'Computer Networks',
    code: 'IT401',
    year: 'SE',
    semester: 'IV',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. V. K. Singh']
  },
  {
    id: 'se4_cn_lab',
    name: 'Computer Networks Lab',
    code: 'IT401L',
    year: 'SE',
    semester: 'IV',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. V. K. Singh']
  },
  {
    id: 'se4_at',
    name: 'Automata Theory',
    code: 'IT402',
    year: 'SE',
    semester: 'IV',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. V. K. Singh']
  },
  {
    id: 'se4_wp',
    name: 'Web Programming',
    code: 'IT403',
    year: 'SE',
    semester: 'IV',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. S. K. Sharma']
  },
  {
    id: 'se4_wp_lab',
    name: 'Web Programming Lab',
    code: 'IT403L',
    year: 'SE',
    semester: 'IV',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. S. K. Sharma']
  },
  {
    id: 'se4_coa',
    name: 'Computer Organization and Architecture',
    code: 'IT404',
    year: 'SE',
    semester: 'IV',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. S. K. Sharma']
  },
  {
    id: 'se4_mp_lab',
    name: 'Microprocessor Lab',
    code: 'IT404L',
    year: 'SE',
    semester: 'IV',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. S. K. Sharma']
  },
  {
    id: 'se4_itc',
    name: 'Information Theory and Coding',
    code: 'IT405',
    year: 'SE',
    semester: 'IV',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. N. S. Kulkarni']
  },
  {
    id: 'se4_math4',
    name: 'Engineering Mathematics-IV',
    code: 'MATH401',
    year: 'SE',
    semester: 'IV',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. N. S. Kulkarni']
  },
  {
    id: 'se4_os_lab',
    name: 'Operating System Lab',
    code: 'IT406L',
    year: 'SE',
    semester: 'IV',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. V. K. Singh']
  },

  // Third Year (TE) - Semester V
  {
    id: 'te5_ip',
    name: 'Internet Programming (IP)',
    code: 'IT501',
    year: 'TE',
    semester: 'V',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. Sonali Patil (SP)']
  },
  {
    id: 'te5_cns',
    name: 'Computer Network Security (CNS)',
    code: 'IT502',
    year: 'TE',
    semester: 'V',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. A. D. Mhaitre (ADM)']
  },
  {
    id: 'te5_eeb',
    name: 'Entrepreneurship and E-Business (EEB)',
    code: 'IT503',
    year: 'TE',
    semester: 'V',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. N. Y. Mohaskar (NYM)']
  },
  {
    id: 'te5_se',
    name: 'Software Engineering (SE)',
    code: 'IT504',
    year: 'TE',
    semester: 'V',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. Sonali Patil (SP)']
  },
  {
    id: 'te5_adsa',
    name: 'Advanced Data Structures and Analysis (ADSA)',
    code: 'IT505',
    year: 'TE',
    semester: 'V',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. R. A. Jolhe (RAJ)']
  },
  {
    id: 'te5_pce2',
    name: 'Professional Communication & Ethics-II (PCE-II)',
    code: 'IT506',
    year: 'TE',
    semester: 'V',
    type: 'Theory',
    hoursPerWeek: 2,
    faculty: ['Dr. Namita Shah (NS)']
  },
  {
    id: 'te5_security_lab',
    name: 'Security Lab',
    code: 'IT502L',
    year: 'TE',
    semester: 'V',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. A. D. Mhaitre (ADM)']
  },
  {
    id: 'te5_dm_lab',
    name: 'Data Mining Lab',
    code: 'IT507L',
    year: 'TE',
    semester: 'V',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. A. D. Mhaitre (ADM)']
  },
  {
    id: 'te5_prog_lab',
    name: 'Programming Lab',
    code: 'IT501L',
    year: 'TE',
    semester: 'V',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. R. A. Jolhe (RAJ)', 'Mrs. Sonali Patil (SP)']
  },
  {
    id: 'te5_adb_lab',
    name: 'Advanced Database Lab',
    code: 'IT508L',
    year: 'TE',
    semester: 'V',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. Sonali Patil (SP)']
  },

  // Third Year (TE) - Semester VI
  {
    id: 'te6_mad',
    name: 'Mobile Application Development',
    code: 'IT601',
    year: 'TE',
    semester: 'VI',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. N. G. Jamkar (NGJ)']
  },
  {
    id: 'te6_isr',
    name: 'Information Storage and Retrieval',
    code: 'IT602',
    year: 'TE',
    semester: 'VI',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. Harshita D. Bhagwat (HDB)']
  },
  {
    id: 'te6_ds',
    name: 'Distributed Systems',
    code: 'IT603',
    year: 'TE',
    semester: 'VI',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. N. G. Jamkar (NGJ)']
  },
  {
    id: 'te6_cna',
    name: 'Computer Network Administration',
    code: 'IT604',
    year: 'TE',
    semester: 'VI',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. Harshita D. Bhagwat (HDB)']
  },
  {
    id: 'te6_cs',
    name: 'Cyber Security',
    code: 'IT605',
    year: 'TE',
    semester: 'VI',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. K. A. Jadhav (KPR)']
  },
  {
    id: 'te6_system_lab',
    name: 'System Lab',
    code: 'IT603L',
    year: 'TE',
    semester: 'VI',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. N. G. Jamkar (NGJ)', 'Dr. Namita Shah (NS)', 'Mrs. N. Y. Mohaskar (NYM)']
  },
  {
    id: 'te6_software_lab',
    name: 'Software Lab',
    code: 'IT605L',
    year: 'TE',
    semester: 'VI',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. K. A. Jadhav (KPR)', 'Mrs. R. A. Jolhe (RAJ)']
  },

  // Fourth Year (BE) - Semester VII
  {
    id: 'be7_ai',
    name: 'Artificial Intelligence',
    code: 'IT701',
    year: 'BE',
    semester: 'VII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Dr. A. K. Tripathi']
  },
  {
    id: 'be7_ml',
    name: 'Machine Learning',
    code: 'IT702',
    year: 'BE',
    semester: 'VII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Dr. A. K. Tripathi']
  },
  {
    id: 'be7_dwm',
    name: 'Data Warehousing and Mining',
    code: 'IT703',
    year: 'BE',
    semester: 'VII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. S. D. Joshi']
  },
  {
    id: 'be7_bda',
    name: 'Big Data Analytics',
    code: 'IT704',
    year: 'BE',
    semester: 'VII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. S. D. Joshi']
  },
  {
    id: 'be7_hpc',
    name: 'High Performance Computing',
    code: 'IT705',
    year: 'BE',
    semester: 'VII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. R. P. Kulkarni']
  },
  {
    id: 'be7_cc',
    name: 'Cloud Computing',
    code: 'IT706',
    year: 'BE',
    semester: 'VII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. R. P. Kulkarni']
  },
  {
    id: 'be7_ai_lab',
    name: 'AI Lab',
    code: 'IT701L',
    year: 'BE',
    semester: 'VII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Dr. A. K. Tripathi']
  },
  {
    id: 'be7_dm_lab',
    name: 'Data Mining Lab',
    code: 'IT703L',
    year: 'BE',
    semester: 'VII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. S. D. Joshi']
  },
  {
    id: 'be7_hpc_lab',
    name: 'HPC Lab',
    code: 'IT705L',
    year: 'BE',
    semester: 'VII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. R. P. Kulkarni']
  },
  {
    id: 'be7_research_lab',
    name: 'Research Lab',
    code: 'IT707L',
    year: 'BE',
    semester: 'VII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Dr. A. K. Tripathi']
  },

  // Fourth Year (BE) - Semester VIII
  {
    id: 'be8_spm',
    name: 'Software Project Management',
    code: 'IT801',
    year: 'BE',
    semester: 'VIII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Dr. M. N. Patil']
  },
  {
    id: 'be8_hci',
    name: 'Human Computer Interface',
    code: 'IT802',
    year: 'BE',
    semester: 'VIII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Dr. M. N. Patil']
  },
  {
    id: 'be8_ddb',
    name: 'Distributed Database',
    code: 'IT803',
    year: 'BE',
    semester: 'VIII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. K. L. Sharma']
  },
  {
    id: 'be8_an',
    name: 'Advanced Networking',
    code: 'IT804',
    year: 'BE',
    semester: 'VIII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mrs. K. L. Sharma']
  },
  {
    id: 'be8_blockchain',
    name: 'Blockchain',
    code: 'IT805',
    year: 'BE',
    semester: 'VIII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. T. S. Rao']
  },
  {
    id: 'be8_iot',
    name: 'IoT (Internet of Things)',
    code: 'IT806',
    year: 'BE',
    semester: 'VIII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. T. S. Rao']
  },
  {
    id: 'be8_is',
    name: 'Information Security',
    code: 'IT807',
    year: 'BE',
    semester: 'VIII',
    type: 'Theory',
    hoursPerWeek: 4,
    faculty: ['Mr. T. S. Rao']
  },
  {
    id: 'be8_project1',
    name: 'Project Lab I',
    code: 'IT801L',
    year: 'BE',
    semester: 'VIII',
    type: 'Project',
    hoursPerWeek: 4,
    faculty: ['Dr. M. N. Patil']
  },
  {
    id: 'be8_hci_lab',
    name: 'HCI Lab',
    code: 'IT802L',
    year: 'BE',
    semester: 'VIII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Dr. M. N. Patil']
  },
  {
    id: 'be8_ddb_lab',
    name: 'Distributed Database Lab',
    code: 'IT803L',
    year: 'BE',
    semester: 'VIII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mrs. K. L. Sharma']
  },
  {
    id: 'be8_blockchain_lab',
    name: 'Blockchain Lab',
    code: 'IT805L',
    year: 'BE',
    semester: 'VIII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. T. S. Rao']
  },
  {
    id: 'be8_iot_lab',
    name: 'IoT Lab',
    code: 'IT806L',
    year: 'BE',
    semester: 'VIII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. T. S. Rao']
  },
  {
    id: 'be8_security_lab',
    name: 'Security Lab',
    code: 'IT807L',
    year: 'BE',
    semester: 'VIII',
    type: 'Lab',
    hoursPerWeek: 2,
    faculty: ['Mr. T. S. Rao']
  },
  {
    id: 'be8_major_project',
    name: 'Major Project',
    code: 'IT808P',
    year: 'BE',
    semester: 'VIII',
    type: 'Project',
    hoursPerWeek: 6,
    faculty: ['Dr. M. N. Patil', 'Dr. A. K. Tripathi', 'Mrs. K. L. Sharma', 'Mr. T. S. Rao']
  },
  {
    id: 'be8_seminar',
    name: 'Seminar',
    code: 'IT809S',
    year: 'BE',
    semester: 'VIII',
    type: 'Tutorial',
    hoursPerWeek: 2,
    faculty: ['Dr. M. N. Patil', 'Dr. A. K. Tripathi', 'Mrs. K. L. Sharma', 'Mr. T. S. Rao']
  }
];

// Room assignments based on actual DMCE IT Department
export const dmceITRooms = [
  { id: 'room_701', name: 'Room 701', type: 'Lab', description: 'Programming Lab' },
  { id: 'room_702', name: 'Room 702', type: 'Lab', description: 'Software Lab' },
  { id: 'room_703', name: 'Room 703', type: 'Lab', description: 'System Lab/Security Lab' },
  { id: 'room_705', name: 'Room 705', type: 'Classroom', description: 'General Classroom' },
  { id: 'room_710', name: 'Room 710', type: 'Tutorial', description: 'Tutorial Room' },
  { id: 'room_801', name: 'Room 801', type: 'Classroom', description: 'Theory Classroom' },
  { id: 'room_803', name: 'Room 803', type: 'Classroom', description: 'Theory Classroom' },
  { id: 'room_807', name: 'Room 807', type: 'Lab', description: 'Data Mining Lab' },
  { id: 'room_901', name: 'Room 901', type: 'Lab', description: 'Advanced Database Lab' },
  { id: 'room_902', name: 'Room 902', type: 'Lab', description: 'Security Lab/System Lab' }
];

// Subject-Faculty mapping for proficiency setup
export const subjectFacultyMapping = {
  // SE Faculty specializations
  'Mrs. P. R. Desai': ['Engineering Mathematics-III', 'Engineering Mathematics-IV', 'Tutorial Sessions'],
  'Mr. S. K. Sharma': ['Object Oriented Programming with C++', 'Web Programming', 'Computer Organization and Architecture'],
  'Mrs. A. B. Patil': ['Data Structures', 'Database Management System'],
  'Dr. R. M. Joshi': ['Computer Graphics', 'Digital Logic Design and Analysis'],
  'Mr. V. K. Singh': ['Computer Networks', 'Automata Theory', 'Operating System'],
  'Mrs. N. S. Kulkarni': ['Information Theory and Coding', 'Engineering Mathematics-IV'],
  
  // TE Faculty specializations
  'Mrs. A. D. Mhaitre (ADM)': ['Computer Network Security (CNS)', 'Security', 'Data Mining'],
  'Mrs. R. A. Jolhe (RAJ)': ['Advanced Data Structures and Analysis (ADSA)', 'Advanced Development', 'Programming'],
  'Mrs. Sonali Patil (SP)': ['Internet Programming (IP)', 'Software Engineering (SE)', 'Advanced Database'],
  'Dr. Namita Shah (NS)': ['Professional Communication & Ethics-II (PCE-II)', 'System Administration'],
  'Mrs. N. Y. Mohaskar (NYM)': ['Entrepreneurship and E-Business (EEB)', 'System Lab'],
  'Mrs. N. G. Jamkar (NGJ)': ['Mobile Application Development', 'Distributed Systems'],
  'Mrs. Harshita D. Bhagwat (HDB)': ['Information Storage and Retrieval', 'Computer Network Administration'],
  'Mr. K. A. Jadhav (KPR)': ['Cyber Security', 'Advanced Development', 'Software Lab'],
  
  // BE Faculty specializations
  'Dr. A. K. Tripathi': ['Artificial Intelligence', 'Machine Learning', 'Research'],
  'Mrs. S. D. Joshi': ['Data Warehousing and Mining', 'Big Data Analytics'],
  'Mr. R. P. Kulkarni': ['High Performance Computing', 'Cloud Computing'],
  'Dr. M. N. Patil': ['Software Project Management', 'Human Computer Interface', 'Project Management'],
  'Mrs. K. L. Sharma': ['Distributed Database', 'Advanced Networking'],
  'Mr. T. S. Rao': ['Blockchain', 'IoT', 'Information Security']
};

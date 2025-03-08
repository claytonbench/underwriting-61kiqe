import { AnyAction, Reducer } from 'redux'; // v4.2.1
import {
  SchoolState,
  School,
  SchoolDetail,
  Program,
  ProgramDetail,
  SchoolFilters,
  ProgramFilters
} from '../../types/school.types';

/**
 * Initial state for the school management module
 */
const initialState: SchoolState = {
  schools: [],
  selectedSchool: null,
  programs: [],
  selectedProgram: null,
  loading: false,
  error: null,
  totalSchools: 0,
  totalPrograms: 0,
  schoolFilters: {
    status: null,
    name: null,
    state: null
  },
  programFilters: {
    status: null,
    name: null,
    school_id: null
  },
  page: 1,
  pageSize: 10
};

/**
 * School reducer handles all school and program-related actions in the loan management system.
 * This includes CRUD operations for schools and programs, as well as filtering and pagination.
 */
const schoolReducer: Reducer<SchoolState> = (
  state = initialState, 
  action: AnyAction
): SchoolState => {
  switch (action.type) {
    // School fetch actions
    case 'fetchSchools/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'fetchSchools/fulfilled':
      return {
        ...state,
        schools: action.payload.results,
        totalSchools: action.payload.total,
        loading: false,
        error: null
      };
    case 'fetchSchools/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to fetch schools'
      };
    
    // School detail fetch actions
    case 'fetchSchoolById/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'fetchSchoolById/fulfilled':
      return {
        ...state,
        selectedSchool: action.payload,
        loading: false,
        error: null
      };
    case 'fetchSchoolById/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to fetch school details'
      };
    
    // School create actions
    case 'createNewSchool/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'createNewSchool/fulfilled':
      return {
        ...state,
        schools: [...state.schools, action.payload],
        totalSchools: state.totalSchools + 1,
        loading: false,
        error: null
      };
    case 'createNewSchool/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to create school'
      };
    
    // School update actions
    case 'updateExistingSchool/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'updateExistingSchool/fulfilled':
      return {
        ...state,
        schools: state.schools.map(school => 
          school.id === action.payload.id ? action.payload : school
        ),
        // Update selectedSchool if it matches the updated school
        selectedSchool: state.selectedSchool?.id === action.payload.id 
          ? { ...state.selectedSchool, ...action.payload } 
          : state.selectedSchool,
        loading: false,
        error: null
      };
    case 'updateExistingSchool/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to update school'
      };
    
    // School delete actions
    case 'deleteExistingSchool/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'deleteExistingSchool/fulfilled':
      return {
        ...state,
        schools: state.schools.filter(school => school.id !== action.payload),
        totalSchools: state.totalSchools - 1,
        // Clear selectedSchool if it matches the deleted school
        selectedSchool: state.selectedSchool?.id === action.payload 
          ? null 
          : state.selectedSchool,
        loading: false,
        error: null
      };
    case 'deleteExistingSchool/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to delete school'
      };
    
    // Program fetch actions
    case 'fetchPrograms/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'fetchPrograms/fulfilled':
      return {
        ...state,
        programs: action.payload.results,
        totalPrograms: action.payload.total,
        loading: false,
        error: null
      };
    case 'fetchPrograms/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to fetch programs'
      };
    
    // Program fetch by school actions
    case 'fetchProgramsBySchool/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'fetchProgramsBySchool/fulfilled':
      return {
        ...state,
        programs: action.payload.results,
        totalPrograms: action.payload.total,
        loading: false,
        error: null
      };
    case 'fetchProgramsBySchool/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to fetch school programs'
      };
    
    // Program detail fetch actions
    case 'fetchProgramById/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'fetchProgramById/fulfilled':
      return {
        ...state,
        selectedProgram: action.payload,
        loading: false,
        error: null
      };
    case 'fetchProgramById/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to fetch program details'
      };
    
    // Program create actions
    case 'createNewProgram/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'createNewProgram/fulfilled':
      return {
        ...state,
        programs: [...state.programs, action.payload],
        totalPrograms: state.totalPrograms + 1,
        loading: false,
        error: null
      };
    case 'createNewProgram/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to create program'
      };
    
    // Program update actions
    case 'updateExistingProgram/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'updateExistingProgram/fulfilled':
      return {
        ...state,
        programs: state.programs.map(program => 
          program.id === action.payload.id ? action.payload : program
        ),
        // Update selectedProgram if it matches the updated program
        selectedProgram: state.selectedProgram?.id === action.payload.id 
          ? { ...state.selectedProgram, ...action.payload }
          : state.selectedProgram,
        loading: false,
        error: null
      };
    case 'updateExistingProgram/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to update program'
      };
    
    // Program delete actions
    case 'deleteExistingProgram/pending':
      return {
        ...state,
        loading: true,
        error: null
      };
    case 'deleteExistingProgram/fulfilled':
      return {
        ...state,
        programs: state.programs.filter(program => program.id !== action.payload),
        totalPrograms: state.totalPrograms - 1,
        // Clear selectedProgram if it matches the deleted program
        selectedProgram: state.selectedProgram?.id === action.payload 
          ? null 
          : state.selectedProgram,
        loading: false,
        error: null
      };
    case 'deleteExistingProgram/rejected':
      return {
        ...state,
        loading: false,
        error: action.payload || 'Failed to delete program'
      };
    
    // Filter actions
    case 'setSchoolFilters':
      return {
        ...state,
        schoolFilters: action.payload,
        page: 1 // Reset page when filters change
      };
    case 'setProgramFilters':
      return {
        ...state,
        programFilters: action.payload,
        page: 1 // Reset page when filters change
      };
    
    // Reset and clear actions
    case 'resetSchoolState':
      return initialState;
    case 'clearSchoolError':
      return {
        ...state,
        error: null
      };
    
    default:
      return state;
  }
};

export default schoolReducer;
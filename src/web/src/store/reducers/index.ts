# src/web/src/store/reducers/index.ts
```typescript
import { combineReducers } from 'redux'; // redux v4.2.1
import applicationReducer from './applicationReducer';
import authReducer from './authReducer';
import documentReducer from './documentReducer';
import schoolReducer from './schoolReducer';
import userReducer from './userReducer';
import underwritingReducer from './underwritingReducer';
import notificationReducer from './notificationReducer';
import fundingReducer from './fundingReducer';
import qcReducer from './qcReducer';

/**
 * Combines all reducers into a single root reducer.
 * This is the main reducer used by the Redux store.
 *
 * Each reducer manages a specific slice of the application state.
 *
 * @returns The combined root reducer.
 */
const rootReducer = combineReducers({
  auth: authReducer,
  application: applicationReducer,
  document: documentReducer,
  school: schoolReducer,
  user: userReducer,
  underwriting: underwritingReducer,
  notification: notificationReducer,
  funding: fundingReducer,
  qc: qcReducer,
});

export default rootReducer;
export {
    applicationReducer,
    authReducer,
    documentReducer,
    schoolReducer,
    userReducer,
    underwritingReducer,
    notificationReducer,
    fundingReducer,
    qcReducer
};
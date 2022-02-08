import { checkDataType } from './getDataType';
// 抛出接口异常
export const errorHandler = (error, instance) => {
  if (checkDataType(error) === 'Object' && error.status === 401) {
    return false;
  }
  let msg = '';
  if (error && error.data && error.data.msg) {
    msg = error.data.msg;
  } else if (error && error.message) {
    msg = error.message;
  } else {
    msg = error;
  }
  console.log(error);
  instance.$bkMessage({
    message: msg,
    theme: 'error',
  });
};

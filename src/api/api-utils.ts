import _ from 'lodash';
import store from "@/store";
import axios from "axios";

export default {
  apiBaseUrl: () => store.getters['context/apiBaseUrl'],
  postMultipartFormData: (
    path: string,
    data: object
  ) => {
    const formData = new FormData();
    _.each(data, (value, key) => {
      formData.append(key, value);
    });
    const apiBaseUrl = store.getters['context/apiBaseUrl'];
    return axios
        .post(
            `${apiBaseUrl}${path}`,
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
        .then(response => response.data);
  }
};

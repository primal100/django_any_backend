from django.db.backends.base.creation import BaseDatabaseCreation

class DatabaseCreation(BaseDatabaseCreation):

    def _get_test_db_name(self):
        return self.connection.settings_dict['TEST']['NAME']

    def _create_test_db(self, verbosity, autoclobber, keepdb=False):
        """
        Internal implementation - creates the test db tables.
        """
        test_database_name = self._get_test_db_name()

        if keepdb:
            return test_database_name

        qn = self.connection.ops.quote_name

        params = {
            'func': self.connection.client.initialize_new,
            'enter_func': self.connection.client.enter,
            'exit_func': self.connection.client.close
        }

        # Create the test database and connect to it.
        with self._nodb_connection.cursor() as cursor:
            try:
                cursor.execute(
                    "CREATE DATABASE %s " % test_database_name, params=params)
            except Exception as e:
                # if we want to keep the db, then no need to do any of the below,
                # just return and skip it all.
                if keepdb:
                    return test_database_name

                sys.stderr.write(
                    "Got an error creating the test database: %s\n" % e)
                if not autoclobber:
                    confirm = input(
                        "Type 'yes' if you would like to try deleting the test "
                        "database '%s', or 'no' to cancel: " % test_database_name)
                if autoclobber or confirm == 'yes':
                    try:
                        if verbosity >= 1:
                            print("Destroying old test database for alias %s..." % (
                                self._get_database_display_str(verbosity, test_database_name),
                            ))
                        cursor.execute(
                            "DROP DATABASE %s" % qn(test_database_name))
                        cursor.execute(
                            "CREATE DATABASE %s %s" % (qn(test_database_name),
                                                       suffix))
                    except Exception as e:
                        sys.stderr.write(
                            "Got an error recreating the test database: %s\n" % e)
                        sys.exit(2)
                else:
                    print("Tests cancelled.")
                    sys.exit(1)

        return test_database_name

    def test_db_signature(self):
        """
        Returns a tuple with elements of self.connection.settings_dict (a
        DATABASES setting value) that uniquely identify a database
        accordingly to the RDBMS particularities.
        """
        settings_dict = self.connection.settings_dict
        return (
            settings_dict['ENGINE'],
            settings_dict['NAME']
        )

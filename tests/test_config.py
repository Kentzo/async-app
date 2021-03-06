import typing
import unittest.mock

from async_app.config import Config, ChainConfig, Option, ConfigOption, _HAS_PYTYPES


WITH_TYPE_CHECK = True
try:
    import typeguard
except ImportError:
    try:
        import pytypes
    except ImportError:
        WITH_TYPE_CHECK = False


class TestConfig(unittest.TestCase):
    def test_get_default(self):
        class MyConfig(Config):
            name: str = Option(default='foo')

        with self.subTest('attribute'):
            self.assertEqual(MyConfig().name, 'foo')

        with self.subTest('key'):
            self.assertEqual(MyConfig()['name'], 'foo')

        with self.subTest('data key'):
            with self.assertRaises(KeyError):
                MyConfig().data['name']

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_get_default_None(self):
        class MyConfig(Config):
            name: str = Option()

        with self.subTest('attribute'):
            with self.assertRaises(TypeError):
                MyConfig().name

        with self.subTest('key'):
            with self.assertRaises(TypeError):
                MyConfig()['name']

        with self.subTest('data key'):
            with self.assertRaises(KeyError):
                MyConfig().data['name']

    def test_get_default_callable(self):
        def default():
            return 'foo'

        class MyConfig(Config):
            name: str = Option(default=default)

        with self.subTest('attribute'):
            self.assertEqual(MyConfig().name, 'foo')

        with self.subTest('key'):
            self.assertEqual(MyConfig()['name'], 'foo')

        with self.subTest('data key'):
            with self.assertRaises(KeyError):
                MyConfig().data['name']

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_set(self):
        class MyConfig(Config):
            name: str = Option(default='foo')

        with self.subTest('attribute'):
            with self.assertRaises(TypeError):
                MyConfig().name = 42

            c = MyConfig()
            c.name = 'bar'
            self.assertEqual(c.name, 'bar')

        with self.subTest('key'):
            with self.assertRaises(TypeError):
                MyConfig()['name'] = 42

            c = MyConfig()
            c['name'] = 'bar'
            self.assertEqual(c.name, 'bar')

        with self.subTest('data key'):
            c = MyConfig()
            c.data['name'] = 42
            self.assertEqual(c.name, 42)
            c.data['name'] = 'bar'
            self.assertEqual(c.name, 'bar')

    def test_get(self):
        class MyConfig(Config):
            name: str = Option(default='foo')

        c = MyConfig(name='bar')

        with self.subTest('attribute'):
            self.assertEqual(c.name, 'bar')

        with self.subTest('key'):
            self.assertEqual(c['name'], 'bar')

        with self.subTest('data key'):
            self.assertEqual(c['name'], 'bar')

    def test_del(self):
        class MyConfig(Config):
            name: str = Option(default='foo')

        with self.subTest('attribute'):
            c = MyConfig()
            c.name = 'bar'
            del c.name
            self.assertEqual(c.name, 'foo')

        with self.subTest('key'):
            c = MyConfig()
            c.name = 'bar'
            del c['name']
            self.assertEqual(c.name, 'foo')

        with self.subTest('data key'):
            c = MyConfig()
            c.name = 'bar'
            del c.data['name']
            self.assertEqual(c.name, 'foo')

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_check_default_value(self):
        with self.assertRaises(TypeError):
            class MyConfig(Config):
                name: str = Option(default=42)

            MyConfig().name

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_check_initialdata(self):
        class MyConfig(Config):
            name: str = Option(default='foo')

        with self.assertRaises(TypeError):
            MyConfig(name=42)

    def test_doc_passed(self):
        class MyConfig(Config):
            name: str = Option(default='foo', doc='bar')

        self.assertEqual(MyConfig.name.__doc__, 'bar')

    def test_inheritance(self):
        class MyConfig(Config):
            first_name: str = Option(default='foo')

        class SubConfig(MyConfig):
            last_name: str = Option(default='bar')

        c = SubConfig()
        self.assertEqual(c.first_name, 'foo')
        self.assertEqual(c.last_name, 'bar')

    def test_override(self):
        class MyConfig(Config):
            first_name: str = Option(default='foo')

        class SubConfig(MyConfig):
            first_name: str = Option(default='bar')

        self.assertEqual(SubConfig().first_name, 'bar')

    def test_override_mismatch_attribute(self):
        with self.subTest('subclass'):
            class MyConfig(Config):
                first_name: str = Option('name')

            with self.assertRaises(AttributeError):
                class SubConfig(MyConfig):
                    last_name: str = Option('name')

        with self.subTest('redefinition'):
            with self.assertRaises(AttributeError):
                class MyConfig(Config):
                    first_name: str = Option('first_name')
                    last_name: str = Option('first_name')

    def test_override_mismatch_name(self):
        with self.subTest('subclass'):
            class MyConfig(Config):
                first_name: str = Option('first_name')

            with self.assertRaises(AttributeError):
                class SubConfig(MyConfig):
                    first_name: str = Option('last_name')

    def test_optional(self):
        class MyConfig(Config):
            name: typing.Optional[str] = Option()

        self.assertIsNone(MyConfig().name)

    def test_no_type(self):
        class MyConfig(Config):
            first_name = Option()
            last_name: typing.Any = Option()

        c = MyConfig()

        c.first_name = 'foo'
        c.last_name = 'bar'
        self.assertEqual(c.first_name, 'foo')
        self.assertEqual(c.last_name, 'bar')

        c.first_name = 42
        c.last_name = 9000
        self.assertEqual(c.first_name, 42)
        self.assertEqual(c.last_name, 9000)

    def test_name_is_optional(self):
        class MyConfig(Config):
            name: str = Option()

        self.assertEqual(MyConfig.name.name, 'name')

    def test_type(self):
        class MyConfig(Config):
            name: str = Option()

        self.assertIs(MyConfig.name.type, str)

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_update(self):
        class MyConfig(Config):
            name: str = Option()

        invalid_dict = {'name': 42}
        invalid_items = [('name', 42)]
        valid_dict = {'name': 'foo'}
        valid_items = [('name', 'foo')]

        with self.assertRaises(TypeError):
            MyConfig().update(**invalid_dict)

        with self.assertRaises(TypeError):
            MyConfig().update(invalid_dict)

        with self.assertRaises(TypeError):
            MyConfig().update(invalid_items)

        MyConfig().update(valid_dict)
        MyConfig().update(valid_items)

        with self.assertRaises(TypeError):
            MyConfig().update(valid_dict, **invalid_dict)

        with self.assertRaises(TypeError):
            MyConfig().update(valid_items, **invalid_dict)

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_check_type(self):
        class MyConfig(Config):
            name: str = Option()

        c = MyConfig()

        with self.subTest('option'):
            with self.assertRaises(TypeError):
                c.check_type('name', 42)

        with self.subTest('not option'):
            c.check_type('age', 42)
            c.check_type('age', 'foo')

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_check_type_not_called_more_than_needed(self):
        with self.subTest('__init_subclass__'):
            with unittest.mock.patch.object(Config, 'check_type', wraps=Config.check_type) as check_type_mock:
                check_type_mock.reset_mock()
                class MyConfig(Config):
                    name: str = Option(default='foo')
                check_type_mock.assert_not_called()

                check_type_mock.reset_mock()
                class MyConfig(Config):
                    name: str = Option()
                check_type_mock.assert_not_called()

        class MyConfig(Config):
            name: str = Option()

        check_type_mock = unittest.mock.MagicMock(wraps=MyConfig.check_type)
        MyConfig.check_type = check_type_mock

        with self.subTest('init'):
            check_type_mock.reset_mock()
            MyConfig(name='bar')
            check_type_mock.assert_called_once_with('name', 'bar', attr_name='name')
            check_type_mock.reset_mock()
            MyConfig(age=42)
            check_type_mock.assert_not_called()

        with self.subTest('get default'):
            check_type_mock.reset_mock()
            c = MyConfig()
            with self.assertRaises(TypeError):
                c.name
            check_type_mock.assert_called_once_with('name[default]', None, attr_name='name')

            check_type_mock.reset_mock()
            def default():
                return 'foo'
            class MyConfig(MyConfig):
                name: str = Option(default=default)
            c = MyConfig()
            c.name
            check_type_mock.assert_has_calls([
                unittest.mock.call('name[default]', default, attr_name='name'),
                unittest.mock.call('name[default]', 'foo', attr_name='name')
            ])

        with self.subTest('get attr'):
            c = MyConfig(name='foo')
            check_type_mock.reset_mock()
            c.name
            check_type_mock.assert_not_called()

        with self.subTest('get key'):
            c = MyConfig(name='foo', bar='baz')
            check_type_mock.reset_mock()
            c['name']
            c['bar']
            check_type_mock.assert_not_called()

        with self.subTest('get data key'):
            c = MyConfig(name='foo', bar='baz')
            check_type_mock.reset_mock()
            c.data['name']
            c.data['bar']
            check_type_mock.assert_not_called()

        with self.subTest('set attr'):
            check_type_mock.reset_mock()
            c = MyConfig()
            c.name = 'foo'
            check_type_mock.assert_called_once_with('name', 'foo', attr_name='name')

        with self.subTest('set key'):
            check_type_mock.reset_mock()
            c = MyConfig()
            c['name'] = 'foo'
            c['bar'] = 'baz'
            check_type_mock.assert_called_once_with('name', 'foo', attr_name='name')

        with self.subTest('set data key'):
            check_type_mock.reset_mock()
            c = MyConfig()
            c.data['name'] = 'foo'
            c.data['bar'] = 'baz'
            check_type_mock.assert_not_called()

        with self.subTest('del attr'):
            c = MyConfig()
            check_type_mock.reset_mock()
            del c.name
            check_type_mock.assert_not_called()

        with self.subTest('del key'):
            c = MyConfig(name='foo', bar='baz')
            check_type_mock.reset_mock()
            del c['name']
            del c['bar']
            check_type_mock.assert_not_called()

        with self.subTest('del data key'):
            c = MyConfig(name='foo', bar='baz')
            check_type_mock.reset_mock()
            del c.data['name']
            del c.data['bar']
            check_type_mock.assert_not_called()

        with self.subTest('update'):
            c = MyConfig()
            check_type_mock.reset_mock()
            c.update(name='foo', bar='baz')
            check_type_mock.assert_called_once_with('name', 'foo', attr_name='name')


class TestConfigOption(unittest.TestCase):
    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_dict(self):
        class SubConfig(Config):
            o: int = Option()

        class MyConfig(Config):
            sub: SubConfig = ConfigOption()

        c = MyConfig()
        c.sub = {'o': 9000}
        self.assertEqual(c.sub.o, 9000)

        with self.assertRaises(TypeError):
            c.sub = {'o': 'foo'}

    def test_config(self):
        class SubConfig(Config):
            o: int = Option()

        class MyConfig(Config):
            sub: SubConfig = ConfigOption()

        sub = SubConfig(o=9000)
        c = MyConfig()
        c.sub = sub
        self.assertEqual(c.sub.o, 9000)

        self.assertIs(c.sub, sub)
        sub.o = 42
        self.assertEqual(c.sub.o, 42)

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_annotation_required(self):
        with self.assertRaises(TypeError):
            class MyConfig(Config):
                o = ConfigOption()

    def test_doc_from_type(self):
        class SubConfig(Config):
            """foobar"""
            o: int = Option()

        class MyConfig(Config):
            sub: SubConfig = ConfigOption()

        self.assertEqual(MyConfig.sub.__doc__, SubConfig.__doc__)

    @unittest.skipIf(_HAS_PYTYPES, "pytypes fails because it expects class to have the __origin__ attribute")
    def test_default(self):
        class SubConfig(Config):
            o: int = Option(default=42)

        with self.subTest('no default'):
            class MyConfig(Config):
                sub: SubConfig = ConfigOption()

            self.assertEqual(MyConfig().sub.o, 42)

            a = MyConfig()
            a.sub.o = 9000
            b = MyConfig()
            self.assertEqual(b.sub.o, 42)

        with self.subTest('callable'):
            def f():
                return SubConfig()

            class MyConfig(Config):
                sub: SubConfig = ConfigOption(default=f)

            self.assertEqual(MyConfig().sub.o, 42)

        with self.subTest('instance'):
            default = SubConfig()

            class MyConfig(Config):
                sub: SubConfig = ConfigOption(default=default)

            self.assertIsNot(MyConfig().sub, default)

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_get_nested(self):
        class SubConfig(Config):
            o: int = Option(default=42)

        class MyConfig(Config):
            sub: SubConfig = ConfigOption()

        self.assertEqual(MyConfig().get_nested(('sub', 'o')), 42)
        self.assertIsNone(MyConfig().get_nested(('foo',)))
        self.assertIsNone(MyConfig().get_nested(('sub', 'foo')))

        with self.assertRaises(TypeError):
            MyConfig().get_nested(())

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_set_nested(self):
        class SubConfig(Config):
            o: int = Option(default=42)

        class MyConfig(Config):
            sub: SubConfig = ConfigOption()

        c = MyConfig()
        c.set_nested(('sub', 'o'), 9000)
        self.assertEqual(c.sub.o, 9000)

        c = MyConfig()
        c.set_nested(('foo',), 9000)
        self.assertEqual(c['foo'], 9000)

        with self.assertRaises(KeyError):
            MyConfig().set_nested(('bar', 'baz'), 9000)

        with self.assertRaises(TypeError):
            MyConfig().set_nested((), 9000)

    @unittest.skipUnless(WITH_TYPE_CHECK, 'type check is disabled')
    def test_pop_nested(self):
        class SubConfig(Config):
            o: int = Option(default=42)

        class MyConfig(Config):
            sub: SubConfig = ConfigOption()

        c = MyConfig()
        c.sub.o = 9000
        self.assertEqual(c.pop_nested(('sub', 'o')), 9000)
        self.assertEqual(c.sub.o, 42)

        MyConfig().pop_nested(('sub', 'o'))

        with self.assertRaises(KeyError):
            MyConfig().pop_nested(('foo',))

        self.assertEqual(MyConfig().pop_nested(('foo',), 9000), 9000)

        with self.assertRaises(KeyError):
            MyConfig().pop_nested(('sub', 'foo'))

        self.assertEqual(MyConfig().pop_nested(('sub', 'foo'), 9000), 9000)

        with self.assertRaises(TypeError):
            MyConfig().pop_nested(())

        with self.assertRaises(TypeError):
            MyConfig().pop_nested(('sub'), 42, 9000)


class TestChainConfig(unittest.TestCase):
    def test_take_first_value(self):
        class MyConfig(Config):
            name: str = Option(default='Foo')

        self.assertEqual(ChainConfig(MyConfig({'name': 'Bar'}), MyConfig({'name': 'Baz'})).name, 'Bar')

    def test_ignore_default(self):
        class MyConfig(Config):
            name: str = Option(default='Foo')

        self.assertEqual(ChainConfig(MyConfig(), MyConfig({'name': 'Baz'})).name, 'Baz')

    def test_take_first_default(self):
        class AConfig(Config):
            name: str = Option(default='Foo')

        class BConfig(Config):
            name: str = Option(default='Bar')

        self.assertEqual(ChainConfig(AConfig(), BConfig()).name, 'Foo')

    def test_invalid_attr(self):
        class MyConfig(Config):
            name: str = Option(default='Foo')

        with self.assertRaises(AttributeError):
            ChainConfig(MyConfig()).last_name

    def test_invalid_default(self):
        class AConfig(Config):
            name: str = Option()

        class BConfig(Config):
            name: str = Option()

        with self.assertRaises(AttributeError):
            ChainConfig(AConfig(), BConfig()).name

    def test_attr_passthrough(self):
        class AConfig(Config):
            first_name: str = Option(default='Foo')

        class BConfig(Config):
            last_name: str = Option(default='Bar')

        with self.subTest('default'):
            self.assertEqual(ChainConfig(AConfig(), BConfig()).last_name, 'Bar')

        with self.subTest('set'):
            self.assertEqual(ChainConfig(AConfig(), BConfig(last_name='Baz')).last_name, 'Baz')

    def test_attr_passthrough_ignores_dictvalues(self):
        class AConfig(Config):
            first_name: str = Option(default='Foo')

        class BConfig(Config):
            last_name: str = Option(default='Bar')

        self.assertEqual(ChainConfig(AConfig(last_name='quux'), BConfig(last_name='Baz')).last_name, 'Baz')

    def test_attr_passthrough_ignores_invalid_default(self):
        class AConfig(Config):
            first_name: str = Option()

        class BConfig(Config):
            first_name: str = Option(default='Bar')

        self.assertEqual(ChainConfig(AConfig(), BConfig()).first_name, 'Bar')

    def test_attr_passthrough_ignores_attribute_error(self):
        class AConfig(Config):
            first_name: str = Option()

        class BConfig(Config):
            last_name: str = Option()

        class CConfig(Config):
            first_name: str = Option(default='Bar')

        self.assertEqual(ChainConfig(AConfig(), BConfig(), CConfig()).first_name, 'Bar')
